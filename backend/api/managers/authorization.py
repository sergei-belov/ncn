import logging
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.db import Database
from api.managers.common import PmsError, decode_cursor, encode_cursor
from api.services import Services
from models import enum, pydantic


POLICY_VERSION = "v1"
LOGGER = logging.getLogger("ncn_authz.events")
WORKSPACE_ROLE_RANK = {
    enum.WorkspaceRole.MEMBER: 1,
    enum.WorkspaceRole.ADMIN: 2,
    enum.WorkspaceRole.OWNER: 3,
}
PROJECT_ROLE_RANK = {
    enum.ProjectRole.VIEWER: 1,
    enum.ProjectRole.MEMBER: 2,
    enum.ProjectRole.ADMIN: 3,
}


@dataclass(frozen=True)
class PolicyRule:
    """Describe the required persisted role and scope for one named action."""

    scope: enum.AuthorizationScope
    minimum_rank: int
    resource_type: str


POLICY_RULES = {
    "workspace.member.read": PolicyRule(enum.AuthorizationScope.WORKSPACE, 2, "workspace"),
    "workspace.member.manage": PolicyRule(enum.AuthorizationScope.WORKSPACE, 2, "workspace"),
    "project.read": PolicyRule(enum.AuthorizationScope.PROJECT, 1, "project"),
    "project.update": PolicyRule(enum.AuthorizationScope.PROJECT, 3, "project"),
    "project.archive": PolicyRule(enum.AuthorizationScope.PROJECT, 3, "project"),
    "project.member.read": PolicyRule(enum.AuthorizationScope.PROJECT, 1, "project"),
    "project.member.manage": PolicyRule(enum.AuthorizationScope.PROJECT, 3, "project"),
    "project.service.read": PolicyRule(enum.AuthorizationScope.SERVICE, 1, "project"),
    "project.service.manage": PolicyRule(enum.AuthorizationScope.SERVICE, 3, "project"),
    "project.state.manage": PolicyRule(enum.AuthorizationScope.PROJECT, 3, "project"),
    "project.agent.manage": PolicyRule(enum.AuthorizationScope.PROJECT, 3, "project"),
    "project.work_item.read": PolicyRule(enum.AuthorizationScope.PROJECT, 1, "project"),
    "project.work_item.write": PolicyRule(enum.AuthorizationScope.PROJECT, 2, "project"),
    "project.work_item.delete_any": PolicyRule(enum.AuthorizationScope.PROJECT, 3, "project"),
    "project.epic.read": PolicyRule(enum.AuthorizationScope.PROJECT, 1, "project"),
    "project.epic.write": PolicyRule(enum.AuthorizationScope.PROJECT, 2, "project"),
    "project.epic.delete_any": PolicyRule(enum.AuthorizationScope.PROJECT, 3, "project"),
}


class AuthorizationManager:
    """Manage persisted access relations and evaluate named role policies."""

    @staticmethod
    def _record(operation: str, result: str, reason: str, **metadata) -> None:
        """Emit a privacy-safe authorization operation record.

        Args:
            operation: Stable operation family.
            result: Stable success, denial, or error outcome.
            reason: Stable machine-readable reason.
            **metadata: Safe actor and scope identifiers.
        """

        fields = " ".join(f"{key}={value}" for key, value in sorted(metadata.items()))
        LOGGER.info(
            "operation=%s result=%s reason=%s policy_version=%s %s",
            operation,
            result,
            reason,
            POLICY_VERSION,
            fields,
        )
        Services.collector.record_authorization(operation=operation, result=result, reason=reason)

    @staticmethod
    def _workspace_api(membership: pydantic.WorkspaceUserDTO) -> pydantic.WorkspaceMembership:
        """Convert an internal workspace relation to its canonical API model."""

        return pydantic.WorkspaceMembership.model_validate(membership)

    @staticmethod
    def _project_api(membership: pydantic.ProjectUserDTO) -> pydantic.ProjectMembership:
        """Convert an internal project relation to its canonical API model."""

        return pydantic.ProjectMembership.model_validate(membership)

    @staticmethod
    def _service_api(restriction: pydantic.ServiceUserDTO) -> pydantic.ServiceRestriction:
        """Convert an internal service restriction to its canonical API model."""

        return pydantic.ServiceRestriction.model_validate(restriction)

    @staticmethod
    async def _active_user(user_id: UUID, session: AsyncSession) -> pydantic.UserDTO:
        """Load an active mutation target.

        Args:
            user_id: Target application user identifier.
            session: Active transaction.

        Returns:
            The active target user.

        Raises:
            PmsError: If the target is absent or disabled.
        """

        user = await Database.users.get(id=user_id, session=session)
        if user is None:
            raise PmsError(404, "USER_NOT_FOUND", "User not found.")
        if not user.is_active:
            raise PmsError(409, "USER_DISABLED", "The target user is disabled.")
        return user

    @staticmethod
    async def _project_scope(project_id: UUID, session: AsyncSession) -> pydantic.ProjectDTO:
        """Load the current PMS-owned project scope.

        Args:
            project_id: Project identifier to validate.
            session: Active transaction.

        Returns:
            Current project data from the owning PMS table.

        Raises:
            PmsError: If the project does not exist.
        """

        project = await Database.projects.get(id=project_id, session=session)
        if project is None:
            raise PmsError(404, "PROJECT_NOT_FOUND", "Project not found.")
        return project

    @staticmethod
    def _workspace_actor(
        memberships: list[pydantic.WorkspaceUserDTO],
        actor_id: UUID,
    ) -> pydantic.WorkspaceUserDTO:
        """Require owner or admin authority in a workspace scope.

        Args:
            memberships: Current workspace relations.
            actor_id: Authenticated actor identifier.

        Returns:
            Actor's qualifying workspace membership.

        Raises:
            PmsError: If the actor lacks workspace administration authority.
        """

        actor = next((item for item in memberships if item.user_id == actor_id), None)
        if actor is None or actor.role not in {enum.WorkspaceRole.OWNER, enum.WorkspaceRole.ADMIN}:
            raise PmsError(403, "FORBIDDEN", "Workspace administration access is required.")
        return actor

    @staticmethod
    def _project_actor(
        memberships: list[pydantic.ProjectUserDTO],
        actor_id: UUID,
        workspace_id: str,
    ) -> pydantic.ProjectUserDTO:
        """Require project-admin authority in a project scope.

        Args:
            memberships: Current project relations.
            actor_id: Authenticated actor identifier.
            workspace_id: PMS-owned parent workspace identifier.

        Returns:
            Actor's qualifying project membership.

        Raises:
            PmsError: If the actor lacks authority or the scope is inconsistent.
        """

        actor = next((item for item in memberships if item.user_id == actor_id), None)
        if actor is None or actor.role != enum.ProjectRole.ADMIN:
            raise PmsError(404, "PROJECT_NOT_FOUND", "Project not found.")
        if actor.workspace_id != workspace_id:
            raise PmsError(422, "SCOPE_MISMATCH", "Project and workspace scope do not match.")
        return actor

    @classmethod
    async def check_authorization(
        cls,
        actor: pydantic.UserDTO,
        data: pydantic.AuthorizationCheckRequest,
    ) -> pydantic.AuthorizationCheckResponse:
        """Evaluate one registered action from current persisted access state.

        The current shared topology authenticates the subject request through
        the normal user boundary, so callers may only request a decision for
        their own persisted user ID.

        Args:
            actor: Authenticated active application user.
            data: Named action and consumer-owned scope reference.

        Returns:
            Current allow or expected-denial response.

        Raises:
            PmsError: If the action is unknown or its scope is malformed.
        """

        if data.user_id != actor.id:
            raise PmsError(403, "CONSUMER_FORBIDDEN", "A decision may only target the current user.")
        rule = POLICY_RULES.get(data.action)
        if rule is None:
            raise PmsError(400, "ACTION_UNKNOWN", "The requested action is not registered.")
        if data.resource is None or data.resource.type != rule.resource_type:
            raise PmsError(400, "SCOPE_INVALID", "The action resource scope is invalid.")

        async with Services.database.session() as session:
            current_user = await Database.users.get(id=data.user_id, session=session)
            if current_user is None or not current_user.is_active:
                response = pydantic.AuthorizationCheckResponse(
                    allowed=False,
                    reason=enum.AuthorizationDecisionReason.USER_DISABLED,
                    effective_role=None,
                    effective_scope=None,
                    policy_version=POLICY_VERSION,
                )
            elif rule.scope == enum.AuthorizationScope.WORKSPACE:
                response = await cls._check_workspace(rule, data, session)
            else:
                response = await cls._check_project(rule, data, session)
        cls._record(
            "decision",
            "allow" if response.allowed else "deny",
            response.reason.value,
            action=data.action,
            user_id=data.user_id,
            workspace_id=data.workspace_id,
            project_id=data.project_id,
            service_id=data.service_id,
        )
        return response

    @staticmethod
    async def _check_workspace(
        rule: PolicyRule,
        data: pydantic.AuthorizationCheckRequest,
        session: AsyncSession,
    ) -> pydantic.AuthorizationCheckResponse:
        """Evaluate a workspace-scoped policy rule.

        Args:
            rule: Registered action rule.
            data: Validated decision request.
            session: Active read transaction.

        Returns:
            Current workspace decision.

        Raises:
            PmsError: If required or forbidden scope fields are inconsistent.
        """

        if data.workspace_id is None or data.project_id is not None or data.service_id is not None:
            raise PmsError(400, "SCOPE_INVALID", "Workspace action scope is invalid.")
        if data.resource is None or data.resource.id != data.workspace_id:
            raise PmsError(400, "SCOPE_INVALID", "Workspace resource does not match its scope.")
        membership = await Database.workspace_users.get(
            workspace_id=data.workspace_id,
            user_id=data.user_id,
            session=session,
        )
        if membership is None:
            return pydantic.AuthorizationCheckResponse(
                allowed=False,
                reason=enum.AuthorizationDecisionReason.NO_MEMBERSHIP,
                effective_role=None,
                effective_scope=enum.AuthorizationScope.WORKSPACE,
                policy_version=POLICY_VERSION,
            )
        allowed = WORKSPACE_ROLE_RANK[membership.role] >= rule.minimum_rank
        return pydantic.AuthorizationCheckResponse(
            allowed=allowed,
            reason=(
                enum.AuthorizationDecisionReason.ROLE_ALLOWED
                if allowed
                else enum.AuthorizationDecisionReason.ROLE_INSUFFICIENT
            ),
            effective_role=membership.role,
            effective_scope=enum.AuthorizationScope.WORKSPACE,
            policy_version=POLICY_VERSION,
        )

    @staticmethod
    async def _check_project(
        rule: PolicyRule,
        data: pydantic.AuthorizationCheckRequest,
        session: AsyncSession,
    ) -> pydantic.AuthorizationCheckResponse:
        """Evaluate a project- or service-scoped policy rule.

        Args:
            rule: Registered action rule.
            data: Validated decision request.
            session: Active read transaction.

        Returns:
            Current project or service decision.

        Raises:
            PmsError: If required scope fields or relationships are invalid.
        """

        if data.workspace_id is None or data.project_id is None:
            raise PmsError(400, "SCOPE_INVALID", "Project action scope is invalid.")
        if data.resource is None or data.resource.id != str(data.project_id):
            raise PmsError(400, "SCOPE_INVALID", "Project resource does not match its scope.")
        if rule.scope == enum.AuthorizationScope.SERVICE and data.service_id is None:
            raise PmsError(400, "SCOPE_INVALID", "Service action requires a service scope.")
        if rule.scope != enum.AuthorizationScope.SERVICE and data.service_id is not None:
            raise PmsError(400, "SCOPE_INVALID", "Project action does not accept a service scope.")
        project = await Database.projects.get(id=data.project_id, session=session)
        if project is None or project.workspace_slug != data.workspace_id:
            return pydantic.AuthorizationCheckResponse(
                allowed=False,
                reason=enum.AuthorizationDecisionReason.SCOPE_MISMATCH,
                effective_role=None,
                effective_scope=rule.scope,
                policy_version=POLICY_VERSION,
            )
        membership = await Database.project_users.get(
            project_id=data.project_id,
            workspace_id=data.workspace_id,
            user_id=data.user_id,
            session=session,
        )
        if membership is None:
            return pydantic.AuthorizationCheckResponse(
                allowed=False,
                reason=enum.AuthorizationDecisionReason.NO_MEMBERSHIP,
                effective_role=None,
                effective_scope=rule.scope,
                policy_version=POLICY_VERSION,
            )
        effective_role = membership.role
        if rule.scope == enum.AuthorizationScope.SERVICE:
            restriction = await Database.service_users.get(
                project_user_id=membership.id,
                service_id=data.service_id,
                session=session,
            )
            if restriction is not None:
                if PROJECT_ROLE_RANK[restriction.role] > PROJECT_ROLE_RANK[membership.role]:
                    raise PmsError(503, "POLICY_UNAVAILABLE", "Stored service access is inconsistent.")
                effective_role = restriction.role
        allowed = PROJECT_ROLE_RANK[effective_role] >= rule.minimum_rank
        return pydantic.AuthorizationCheckResponse(
            allowed=allowed,
            reason=(
                enum.AuthorizationDecisionReason.ROLE_ALLOWED
                if allowed
                else enum.AuthorizationDecisionReason.ROLE_INSUFFICIENT
            ),
            effective_role=effective_role,
            effective_scope=rule.scope,
            policy_version=POLICY_VERSION,
        )

    @classmethod
    async def list_workspace_members(
        cls,
        workspace_id: str,
        actor: pydantic.UserDTO,
        queries: pydantic.MembershipListQueries,
    ) -> pydantic.WorkspaceMembershipList:
        """List workspace memberships for an authorized administrator.

        Args:
            workspace_id: Workspace scope to list.
            actor: Authenticated user requesting the list.
            queries: Bounded cursor and search options.

        Returns:
            Stable cursor page of workspace memberships.
        """

        offset = decode_cursor(queries.cursor)
        async with Services.database.session() as session:
            memberships = await Database.workspace_users.get_list(
                workspace_id=workspace_id,
                session=session,
            )
            cls._workspace_actor(memberships, actor.id)
            rows, total = await Database.workspace_users.list_with_details(
                workspace_id=workspace_id,
                offset=offset,
                limit=queries.limit,
                search=queries.search,
                session=session,
            )
        items = [
            pydantic.WorkspaceMembershipItem(
                **row.model_dump(exclude={"email", "name", "is_active"}),
                user=pydantic.AccessUserSummary(
                    id=row.user_id,
                    email=row.email,
                    name=row.name,
                    is_active=row.is_active,
                ),
            )
            for row in rows
        ]
        next_offset = offset + len(items)
        return pydantic.WorkspaceMembershipList(
            items=items,
            next_cursor=encode_cursor(next_offset) if next_offset < total else None,
        )

    @classmethod
    async def create_workspace_member(
        cls,
        workspace_id: str,
        actor: pydantic.UserDTO,
        data: pydantic.CreateWorkspaceMembershipRequest,
    ) -> pydantic.WorkspaceMembership:
        """Grant a role within an established workspace access scope.

        Args:
            workspace_id: Workspace receiving the membership.
            actor: Authenticated workspace administrator.
            data: Target user and desired role.

        Returns:
            Newly created canonical membership.

        Raises:
            PmsError: If scope, target, ceiling, owner, or uniqueness guards fail.
        """

        async with Services.database.session() as session:
            memberships = await Database.workspace_users.get_list(
                workspace_id=workspace_id,
                session=session,
            )
            actor_membership = cls._workspace_actor(memberships, actor.id)
            await cls._active_user(data.user_id, session)
            if data.role == enum.WorkspaceRole.OWNER:
                raise PmsError(
                    409,
                    "OWNER_TRANSFER_REQUIRED",
                    "Owner changes require the separately approved transfer operation.",
                )
            if WORKSPACE_ROLE_RANK[data.role] > WORKSPACE_ROLE_RANK[actor_membership.role]:
                raise PmsError(403, "ROLE_EXCEEDS_ACTOR", "The requested role exceeds actor authority.")
            created = await Database.workspace_users.upsert(
                data=pydantic.WorkspaceUserCreateDTO(
                    workspace_id=workspace_id,
                    user_id=data.user_id,
                    role=data.role,
                ),
                conflict_fields={"workspace_id", "user_id"},
                on_conflict="nothing",
                session=session,
                mode="json",
            )
            if created is None:
                raise PmsError(409, "MEMBERSHIP_EXISTS", "Workspace membership already exists.")
        cls._record(
            "workspace_membership_create",
            "success",
            "ROLE_ASSIGNED",
            actor_id=actor.id,
            target_user_id=data.user_id,
            workspace_id=workspace_id,
            after_role=data.role.value,
        )
        return cls._workspace_api(created)

    @classmethod
    async def update_workspace_member(
        cls,
        workspace_id: str,
        user_id: UUID,
        actor: pydantic.UserDTO,
        data: pydantic.UpdateWorkspaceMembershipRequest,
    ) -> pydantic.WorkspaceMembership:
        """Change a workspace membership under optimistic and ceiling guards.

        Args:
            workspace_id: Workspace containing the membership.
            user_id: Target member identifier.
            actor: Authenticated workspace administrator.
            data: Desired role and expected current version.

        Returns:
            Updated canonical membership.

        Raises:
            PmsError: If authority, owner policy, or version guards fail.
        """

        async with Services.database.session() as session:
            memberships = await Database.workspace_users.get_list(
                workspace_id=workspace_id,
                session=session,
            )
            actor_membership = cls._workspace_actor(memberships, actor.id)
            target = next((item for item in memberships if item.user_id == user_id), None)
            if target is None:
                raise PmsError(404, "MEMBERSHIP_NOT_FOUND", "Workspace membership not found.")
            await cls._active_user(user_id, session)
            if target.version != data.expected_version:
                raise PmsError(
                    409,
                    "VERSION_CONFLICT",
                    "Workspace membership changed since it was read.",
                    current=cls._workspace_api(target).model_dump(),
                )
            if target.role == enum.WorkspaceRole.OWNER or data.role == enum.WorkspaceRole.OWNER:
                if target.role == enum.WorkspaceRole.OWNER:
                    owners = sum(item.role == enum.WorkspaceRole.OWNER for item in memberships)
                    if owners <= 1 and data.role != enum.WorkspaceRole.OWNER:
                        raise PmsError(409, "LAST_WORKSPACE_OWNER", "The last workspace owner is protected.")
                raise PmsError(
                    409,
                    "OWNER_TRANSFER_REQUIRED",
                    "Owner changes require the separately approved transfer operation.",
                )
            if WORKSPACE_ROLE_RANK[data.role] > WORKSPACE_ROLE_RANK[actor_membership.role]:
                raise PmsError(403, "ROLE_EXCEEDS_ACTOR", "The requested role exceeds actor authority.")
            updated = await Database.workspace_users.update(
                id=target.id,
                data=pydantic.WorkspaceUserUpdateFieldsDTO(
                    role=data.role,
                    version=target.version + 1,
                ),
                version=data.expected_version,
                session=session,
                mode="json",
            )
            if updated is None:
                raise PmsError(409, "VERSION_CONFLICT", "Workspace membership changed concurrently.")
        cls._record(
            "workspace_membership_update",
            "success",
            "ROLE_CHANGED",
            actor_id=actor.id,
            target_user_id=user_id,
            workspace_id=workspace_id,
            before_role=target.role.value,
            after_role=data.role.value,
        )
        return cls._workspace_api(updated)

    @classmethod
    async def revoke_workspace_member(
        cls,
        workspace_id: str,
        user_id: UUID,
        actor: pydantic.UserDTO,
        data: pydantic.RevokeMembershipRequest,
    ) -> None:
        """Revoke a workspace membership without removing protected owners.

        Args:
            workspace_id: Workspace containing the membership.
            user_id: Target member identifier.
            actor: Authenticated workspace administrator.
            data: Expected current membership version.

        Raises:
            PmsError: If authority, owner, or version guards fail.
        """

        async with Services.database.session() as session:
            memberships = await Database.workspace_users.get_list(
                workspace_id=workspace_id,
                session=session,
            )
            cls._workspace_actor(memberships, actor.id)
            target = next((item for item in memberships if item.user_id == user_id), None)
            if target is None:
                raise PmsError(404, "MEMBERSHIP_NOT_FOUND", "Workspace membership not found.")
            if target.version != data.expected_version:
                raise PmsError(
                    409,
                    "VERSION_CONFLICT",
                    "Workspace membership changed since it was read.",
                    current=cls._workspace_api(target).model_dump(),
                )
            if target.role == enum.WorkspaceRole.OWNER:
                owners = sum(item.role == enum.WorkspaceRole.OWNER for item in memberships)
                code = "LAST_WORKSPACE_OWNER" if owners <= 1 else "OWNER_TRANSFER_REQUIRED"
                raise PmsError(409, code, "Workspace owners cannot be revoked by this operation.")
            deleted = await Database.workspace_users.delete(
                id=target.id,
                version=data.expected_version,
                session=session,
            )
            if deleted is None:
                raise PmsError(409, "VERSION_CONFLICT", "Workspace membership changed concurrently.")
        cls._record(
            "workspace_membership_revoke",
            "success",
            "MEMBERSHIP_REVOKED",
            actor_id=actor.id,
            target_user_id=user_id,
            workspace_id=workspace_id,
            before_role=target.role.value,
        )

    @classmethod
    async def list_project_members(
        cls,
        project_id: UUID,
        actor: pydantic.UserDTO,
        queries: pydantic.MembershipListQueries,
    ) -> pydantic.ProjectMembershipList:
        """List project members and explicit service restrictions for an admin.

        Args:
            project_id: Project scope to list.
            actor: Authenticated user requesting the list.
            queries: Bounded cursor and search options.

        Returns:
            Stable cursor page of enriched project memberships.
        """

        offset = decode_cursor(queries.cursor)
        async with Services.database.session() as session:
            project = await cls._project_scope(project_id, session)
            memberships = await Database.project_users.get_list(project_id=project_id, session=session)
            cls._project_actor(memberships, actor.id, project.workspace_slug)
            rows, total = await Database.project_users.list_with_details(
                project_id=project_id,
                offset=offset,
                limit=queries.limit,
                search=queries.search,
                session=session,
            )
            restrictions = await Database.service_users.get_list(
                project_user_id=[row.id for row in rows],
                sort_by="service_id",
                session=session,
            )
        by_membership: dict[UUID, list[pydantic.ServiceRestriction]] = {
            row.id: [] for row in rows
        }
        for restriction in restrictions:
            by_membership[restriction.project_user_id].append(cls._service_api(restriction))
        items = [
            pydantic.ProjectMembershipItem(
                **row.model_dump(
                    exclude={"display_name", "email", "avatar_url", "is_active"}
                ),
                user=pydantic.AccessUserSummary(
                    id=row.user_id,
                    email=row.email,
                    name=row.display_name,
                    is_active=row.is_active,
                ),
                service_restrictions=by_membership[row.id],
            )
            for row in rows
        ]
        next_offset = offset + len(items)
        return pydantic.ProjectMembershipList(
            items=items,
            next_cursor=encode_cursor(next_offset) if next_offset < total else None,
        )

    @classmethod
    async def create_project_member(
        cls,
        project_id: UUID,
        actor: pydantic.UserDTO,
        data: pydantic.CreateProjectMembershipRequest,
    ) -> pydantic.ProjectMembership:
        """Grant a project role under current admin and uniqueness guards.

        Args:
            project_id: Project receiving the membership.
            actor: Authenticated project administrator.
            data: Target user and desired role.

        Returns:
            Newly created canonical project membership.

        Raises:
            PmsError: If scope, user, authority, or uniqueness guards fail.
        """

        async with Services.database.session() as session:
            project = await cls._project_scope(project_id, session)
            memberships = await Database.project_users.get_list(
                project_id=project_id,
                session=session,
            )
            actor_membership = cls._project_actor(memberships, actor.id, project.workspace_slug)
            await cls._active_user(data.user_id, session)
            if PROJECT_ROLE_RANK[data.role] > PROJECT_ROLE_RANK[actor_membership.role]:
                raise PmsError(403, "ROLE_EXCEEDS_ACTOR", "The requested role exceeds actor authority.")
            created = await Database.project_users.upsert(
                data=pydantic.ProjectUserCreateDTO(
                    project_id=project_id,
                    workspace_id=project.workspace_slug,
                    user_id=data.user_id,
                    role=data.role,
                    source=enum.ProjectMembershipSource.MANUAL,
                ),
                conflict_fields={"project_id", "user_id"},
                on_conflict="nothing",
                session=session,
                mode="json",
            )
            if created is None:
                raise PmsError(409, "MEMBERSHIP_EXISTS", "Project membership already exists.")
        cls._record(
            "project_membership_create",
            "success",
            "ROLE_ASSIGNED",
            actor_id=actor.id,
            target_user_id=data.user_id,
            workspace_id=project.workspace_slug,
            project_id=project_id,
            after_role=data.role.value,
        )
        return cls._project_api(created)

    @classmethod
    async def update_project_member(
        cls,
        project_id: UUID,
        user_id: UUID,
        actor: pydantic.UserDTO,
        data: pydantic.UpdateProjectMembershipRequest,
    ) -> pydantic.ProjectMembership:
        """Change a project role under admin, version, and last-admin guards.

        Args:
            project_id: Project containing the membership.
            user_id: Target member identifier.
            actor: Authenticated project administrator.
            data: Desired role and expected current version.

        Returns:
            Updated canonical project membership.

        Raises:
            PmsError: If authority, version, admin coverage, or service guards fail.
        """

        async with Services.database.session() as session:
            project = await cls._project_scope(project_id, session)
            memberships = await Database.project_users.get_list(
                project_id=project_id,
                session=session,
            )
            actor_membership = cls._project_actor(memberships, actor.id, project.workspace_slug)
            target = next((item for item in memberships if item.user_id == user_id), None)
            if target is None:
                raise PmsError(404, "MEMBERSHIP_NOT_FOUND", "Project membership not found.")
            await cls._active_user(user_id, session)
            if target.version != data.expected_version:
                raise PmsError(
                    409,
                    "VERSION_CONFLICT",
                    "Project membership changed since it was read.",
                    current=cls._project_api(target).model_dump(),
                )
            if PROJECT_ROLE_RANK[data.role] > PROJECT_ROLE_RANK[actor_membership.role]:
                raise PmsError(403, "ROLE_EXCEEDS_ACTOR", "The requested role exceeds actor authority.")
            admins = sum(item.role == enum.ProjectRole.ADMIN for item in memberships)
            if target.role == enum.ProjectRole.ADMIN and data.role != enum.ProjectRole.ADMIN and admins <= 1:
                raise PmsError(409, "LAST_PROJECT_ADMIN", "The last project admin is protected.")
            restrictions = await Database.service_users.get_list(
                project_user_id=target.id,
                session=session,
            )
            if any(PROJECT_ROLE_RANK[item.role] > PROJECT_ROLE_RANK[data.role] for item in restrictions):
                raise PmsError(
                    409,
                    "SERVICE_RESTRICTION_CONFLICT",
                    "Existing service restrictions exceed the requested project role.",
                )
            updated = await Database.project_users.update(
                id=target.id,
                data=pydantic.ProjectUserUpdateFieldsDTO(
                    role=data.role,
                    version=target.version + 1,
                ),
                version=data.expected_version,
                session=session,
                mode="json",
            )
            if updated is None:
                raise PmsError(409, "VERSION_CONFLICT", "Project membership changed concurrently.")
        cls._record(
            "project_membership_update",
            "success",
            "ROLE_CHANGED",
            actor_id=actor.id,
            target_user_id=user_id,
            workspace_id=project.workspace_slug,
            project_id=project_id,
            before_role=target.role.value,
            after_role=data.role.value,
        )
        return cls._project_api(updated)

    @classmethod
    async def revoke_project_member(
        cls,
        project_id: UUID,
        user_id: UUID,
        actor: pydantic.UserDTO,
        data: pydantic.RevokeMembershipRequest,
    ) -> None:
        """Revoke project access under optimistic and last-admin guards.

        Args:
            project_id: Project containing the membership.
            user_id: Target member identifier.
            actor: Authenticated project administrator.
            data: Expected current membership version.

        Raises:
            PmsError: If authority, version, or last-admin guards fail.
        """

        async with Services.database.session() as session:
            project = await cls._project_scope(project_id, session)
            memberships = await Database.project_users.get_list(
                project_id=project_id,
                session=session,
            )
            cls._project_actor(memberships, actor.id, project.workspace_slug)
            target = next((item for item in memberships if item.user_id == user_id), None)
            if target is None:
                raise PmsError(404, "MEMBERSHIP_NOT_FOUND", "Project membership not found.")
            if target.version != data.expected_version:
                raise PmsError(
                    409,
                    "VERSION_CONFLICT",
                    "Project membership changed since it was read.",
                    current=cls._project_api(target).model_dump(),
                )
            admins = sum(item.role == enum.ProjectRole.ADMIN for item in memberships)
            if target.role == enum.ProjectRole.ADMIN and admins <= 1:
                raise PmsError(409, "LAST_PROJECT_ADMIN", "The last project admin is protected.")
            deleted = await Database.project_users.delete(
                id=target.id,
                version=data.expected_version,
                session=session,
            )
            if deleted is None:
                raise PmsError(409, "VERSION_CONFLICT", "Project membership changed concurrently.")
        cls._record(
            "project_membership_revoke",
            "success",
            "MEMBERSHIP_REVOKED",
            actor_id=actor.id,
            target_user_id=user_id,
            workspace_id=project.workspace_slug,
            project_id=project_id,
            before_role=target.role.value,
        )

    @classmethod
    async def put_service_restriction(
        cls,
        project_id: UUID,
        user_id: UUID,
        service_id: str,
        actor: pydantic.UserDTO,
        data: pydantic.PutServiceRestrictionRequest,
    ) -> tuple[pydantic.ServiceRestrictionResult, bool]:
        """Create or replace an explicit narrowing service role.

        Args:
            project_id: Parent project scope.
            user_id: Target project member.
            service_id: Bounded service identifier.
            actor: Authenticated project administrator.
            data: Desired role and optional existing version.

        Returns:
            Canonical restriction with a flag indicating creation.

        Raises:
            PmsError: If membership, ceiling, uniqueness, or version guards fail.
        """

        async with Services.database.session() as session:
            project = await cls._project_scope(project_id, session)
            memberships = await Database.project_users.get_list(
                project_id=project_id,
                session=session,
            )
            actor_membership = cls._project_actor(memberships, actor.id, project.workspace_slug)
            target = next((item for item in memberships if item.user_id == user_id), None)
            if target is None:
                raise PmsError(409, "PROJECT_MEMBERSHIP_REQUIRED", "Project membership is required.")
            await cls._active_user(user_id, session)
            if (
                PROJECT_ROLE_RANK[data.role] > PROJECT_ROLE_RANK[target.role]
                or PROJECT_ROLE_RANK[data.role] > PROJECT_ROLE_RANK[actor_membership.role]
            ):
                raise PmsError(422, "SERVICE_ROLE_ELEVATION", "Service role cannot elevate access.")
            existing = await Database.service_users.get(
                project_user_id=target.id,
                service_id=service_id,
                session=session,
            )
            if existing is None:
                if data.expected_version is not None:
                    raise PmsError(409, "VERSION_CONFLICT", "Service restriction no longer exists.")
                restriction = await Database.service_users.upsert(
                    data=pydantic.ServiceUserCreateDTO(
                        project_user_id=target.id,
                        service_id=service_id,
                        role=data.role,
                    ),
                    conflict_fields={"project_user_id", "service_id"},
                    on_conflict="nothing",
                    session=session,
                    mode="json",
                )
                if restriction is None:
                    raise PmsError(409, "RESTRICTION_EXISTS", "Service restriction was created concurrently.")
                created = True
            else:
                if data.expected_version is None:
                    if existing.role != data.role:
                        raise PmsError(409, "RESTRICTION_EXISTS", "Service restriction already exists.")
                    restriction = existing
                    created = False
                else:
                    if existing.version != data.expected_version:
                        raise PmsError(
                            409,
                            "VERSION_CONFLICT",
                            "Service restriction changed since it was read.",
                            current=cls._service_api(existing).model_dump(),
                        )
                    if existing.role == data.role:
                        restriction = existing
                    else:
                        restriction = await Database.service_users.update(
                            id=existing.id,
                            data=pydantic.ServiceUserUpdateFieldsDTO(
                                role=data.role,
                                version=existing.version + 1,
                            ),
                            version=data.expected_version,
                            session=session,
                            mode="json",
                        )
                        if restriction is None:
                            raise PmsError(409, "VERSION_CONFLICT", "Service restriction changed concurrently.")
                    created = False
        cls._record(
            "service_restriction_put",
            "success",
            "RESTRICTION_CREATED" if created else "RESTRICTION_UPDATED",
            actor_id=actor.id,
            target_user_id=user_id,
            workspace_id=project.workspace_slug,
            project_id=project_id,
            service_id=service_id,
            after_role=data.role.value,
        )
        return (
            pydantic.ServiceRestrictionResult(
                **cls._service_api(restriction).model_dump(),
                effective_role=restriction.role,
            ),
            created,
        )

    @classmethod
    async def delete_service_restriction(
        cls,
        project_id: UUID,
        user_id: UUID,
        service_id: str,
        actor: pydantic.UserDTO,
        data: pydantic.DeleteServiceRestrictionRequest,
    ) -> None:
        """Remove a service restriction and restore project-role inheritance.

        Args:
            project_id: Parent project scope.
            user_id: Target project member.
            service_id: Restricted service identifier.
            actor: Authenticated project administrator.
            data: Expected current restriction version.

        Raises:
            PmsError: If membership, authority, existence, or version guards fail.
        """

        async with Services.database.session() as session:
            project = await cls._project_scope(project_id, session)
            memberships = await Database.project_users.get_list(
                project_id=project_id,
                session=session,
            )
            cls._project_actor(memberships, actor.id, project.workspace_slug)
            target = next((item for item in memberships if item.user_id == user_id), None)
            if target is None:
                raise PmsError(409, "PROJECT_MEMBERSHIP_REQUIRED", "Project membership is required.")
            restriction = await Database.service_users.get(
                project_user_id=target.id,
                service_id=service_id,
                session=session,
            )
            if restriction is None:
                raise PmsError(404, "RESTRICTION_NOT_FOUND", "Service restriction not found.")
            if restriction.version != data.expected_version:
                raise PmsError(
                    409,
                    "VERSION_CONFLICT",
                    "Service restriction changed since it was read.",
                    current=cls._service_api(restriction).model_dump(),
                )
            deleted = await Database.service_users.delete(
                id=restriction.id,
                version=data.expected_version,
                session=session,
            )
            if deleted is None:
                raise PmsError(409, "VERSION_CONFLICT", "Service restriction changed concurrently.")
        cls._record(
            "service_restriction_delete",
            "success",
            "INHERITANCE_RESTORED",
            actor_id=actor.id,
            target_user_id=user_id,
            workspace_id=project.workspace_slug,
            project_id=project_id,
            service_id=service_id,
            before_role=restriction.role.value,
        )

    @classmethod
    async def bootstrap_creator_access(
        cls,
        project_id: UUID,
        actor: pydantic.UserDTO,
        data: pydantic.BootstrapCreatorAccessRequest,
    ) -> tuple[pydantic.ProjectMembership, bool]:
        """Converge creator-admin access for a PMS-owned project.

        The current shared topology binds bootstrap to the authenticated
        creator and the project's persisted ``created_by`` value. Physical
        service extraction can replace this adapter after workload identity is
        specified.

        Args:
            project_id: PMS-owned project identifier.
            actor: Authenticated creator in the shared deployment.
            data: Parent workspace and creator identifiers.

        Returns:
            Canonical creator membership and a creation flag.

        Raises:
            PmsError: If caller, scope, user, or existing state conflicts.
        """

        if actor.id != data.creator_user_id:
            raise PmsError(403, "PMS_CALLER_FORBIDDEN", "Creator bootstrap may only target the actor.")
        async with Services.database.session() as session:
            project = await cls._project_scope(project_id, session)
            if project.workspace_slug != data.workspace_id:
                raise PmsError(422, "SCOPE_MISMATCH", "Project and workspace scope do not match.")
            if project.created_by != data.creator_user_id:
                raise PmsError(409, "BOOTSTRAP_CONFLICT", "The requested user is not the project creator.")
            await cls._active_user(data.creator_user_id, session)
            memberships = await Database.project_users.get_list(
                project_id=project_id,
                session=session,
            )
            existing = next(
                (item for item in memberships if item.user_id == data.creator_user_id),
                None,
            )
            if existing is not None:
                if existing.role != enum.ProjectRole.ADMIN:
                    raise PmsError(409, "BOOTSTRAP_CONFLICT", "Creator membership is not administrative.")
                membership = existing
                created = False
            else:
                membership = await Database.project_users.upsert(
                    data=pydantic.ProjectUserCreateDTO(
                        project_id=project_id,
                        workspace_id=data.workspace_id,
                        user_id=data.creator_user_id,
                        role=enum.ProjectRole.ADMIN,
                        source=enum.ProjectMembershipSource.BOOTSTRAP,
                    ),
                    conflict_fields={"project_id", "user_id"},
                    on_conflict="nothing",
                    session=session,
                    mode="json",
                )
                if membership is None:
                    raise PmsError(409, "BOOTSTRAP_CONFLICT", "Creator access changed concurrently.")
                created = True
        cls._record(
            "project_creator_bootstrap",
            "success",
            "CREATOR_ADMIN_READY",
            actor_id=actor.id,
            workspace_id=data.workspace_id,
            project_id=project_id,
        )
        return cls._project_api(membership), created
