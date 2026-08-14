from datetime import datetime, timezone
from uuid import UUID

from api.db.db import Database
from api.managers.agents import AgentsManager
from api.managers.common import (
    AccessManager,
    PmsError,
    cursor_meta,
    decode_cursor,
    emit_event,
    permissions_for,
)
from api.services import Services
from models import enum, pydantic
from models.pydantic.api import common_api, project_api


DEFAULT_STATES = (
    ("Бэклог", "#6B7280", enum.StateGroup.BACKLOG, False),
    ("К выполнению", "#A3A3A3", enum.StateGroup.UNSTARTED, True),
    ("В работе", "#F59E0B", enum.StateGroup.STARTED, False),
    ("Готово", "#22C55E", enum.StateGroup.COMPLETED, False),
)


class ProjectsManager:
    """Manage project lifecycle, membership-derived views, and defaults."""

    @staticmethod
    async def _project_api(
        session,
        project: pydantic.ProjectDTO,
        role: enum.ProjectRole,
        summaries: list[common_api.MemberSummary] | None = None,
        work_items_count: int | None = None,
        epics_count: int | None = None,
    ) -> project_api.Project:
        """Build a complete public project representation.

        Args:
            session: Active database session.
            project: Project DTO to expose.
            role: Actor's membership role.
            summaries: Optional preloaded member summaries.
            work_items_count: Optional precomputed work-item count.
            epics_count: Optional precomputed epic count.

        Returns:
            A project enriched with permissions, member preview, and counts.

        Raises:
            PmsError: If the project has no configured default state.
        """
        if summaries is None:
            members = await Database.project_users.get_members_with_details(
                project_ids=[project.id],
                session=session,
            )
            summaries = [
                common_api.MemberSummary(
                    id=member.user_id,
                    display_name=member.display_name,
                    avatar_url=member.avatar_url,
                    is_active=member.is_active,
                )
                for member in members
            ]
        if work_items_count is None:
            work_items_count = await Database.work_items.get_count(
                project_id=project.id,
                session=session,
            )
        if epics_count is None:
            epics_count = await Database.epics.get_count(
                project_id=project.id,
                session=session,
            )
        if project.default_state_id is None:
            raise PmsError(500, "INTERNAL_ERROR", "Project has no default state.")
        return project_api.Project(
            id=project.id,
            workspace_slug=project.workspace_slug,
            name=project.name,
            identifier=project.identifier,
            description=project.description,
            icon=project.icon,
            color=project.color,
            access=project.access,
            role=role,
            permissions=permissions_for(role),
            member_preview=summaries[:3],
            total_members=len(summaries),
            active_work_items_count=work_items_count,
            epics_count=epics_count,
            archived_at=project.archived_at,
            created_at=project.created_at,
            updated_at=project.updated_at,
            version=project.version,
            member_ids=[member.id for member in summaries],
            default_state_id=project.default_state_id,
        )

    @classmethod
    async def list_projects(
        cls,
        workspace_slug: str,
        actor: pydantic.ActorDTO,
        queries: project_api.ProjectListQueries,
    ) -> project_api.ProjectListResponse:
        """List projects visible to an actor in a workspace.

        Args:
            workspace_slug: Workspace whose projects are requested.
            actor: Request actor context.
            queries: Search, status, ownership, sorting, and cursor options.

        Returns:
            A cursor-paginated list of enriched project summaries.

        Raises:
            PmsError: If workspace access or cursor validation fails.
        """
        AccessManager.require_workspace(actor, workspace_slug)
        offset = decode_cursor(queries.cursor)
        async with Services.database.session() as session:
            rows, total = await Database.projects.list_visible(
                session=session,
                workspace_slug=workspace_slug,
                actor_id=actor.id,
                archived=queries.status == enum.ProjectStatus.ARCHIVED,
                mine=queries.mine,
                search=queries.search if queries.search and queries.search.strip() else None,
                sort=queries.sort,
                offset=offset,
                limit=queries.limit,
            )
            project_ids = [pydantic.ProjectDTO.model_validate(row).id for row in rows]
            members = await Database.project_users.get_members_with_details(
                project_ids=project_ids,
                session=session,
            )
            members_by_project: dict[UUID, list[common_api.MemberSummary]] = {
                project_id: [] for project_id in project_ids
            }
            for member in members:
                members_by_project[member.project_id].append(
                    common_api.MemberSummary(
                        id=member.user_id,
                        display_name=member.display_name,
                        avatar_url=member.avatar_url,
                        is_active=member.is_active,
                    )
                )
            items = []
            for row in rows:
                project = pydantic.ProjectDTO.model_validate(row)
                role = enum.ProjectRole(row.member_role)
                summaries = members_by_project[project.id]
                items.append(
                    project_api.ProjectListItem(
                        id=project.id,
                        workspace_slug=project.workspace_slug,
                        name=project.name,
                        identifier=project.identifier,
                        description=project.description,
                        icon=project.icon,
                        color=project.color,
                        access=project.access,
                        role=role,
                        permissions=permissions_for(role),
                        member_preview=summaries[:3],
                        total_members=len(summaries),
                        active_work_items_count=int(row.active_work_items_count),
                        epics_count=int(row.epics_count),
                        archived_at=project.archived_at,
                        created_at=project.created_at,
                        updated_at=project.updated_at,
                        version=project.version,
                    )
                )
        meta = project_api.ProjectListMeta(
            **cursor_meta(offset, queries.limit, len(items), total).model_dump(),
            permissions=common_api.WorkspaceProjectPermissions(can_create_project=True),
        )
        return project_api.ProjectListResponse(data=items, meta=meta)

    @classmethod
    async def create_project(
        cls,
        workspace_slug: str,
        actor: pydantic.ActorDTO,
        data: project_api.CreateProjectRequest,
    ) -> project_api.ProjectResponse:
        """Create a project with membership, default states, and coordinator.

        The client-provided project ID makes creation idempotent for the same
        actor and workspace.

        Args:
            workspace_slug: Workspace receiving the project.
            actor: Request actor and initial project administrator.
            data: Validated project creation fields.

        Returns:
            The existing idempotent result or newly initialized project.

        Raises:
            PmsError: If workspace access fails, the project ID is owned by a
                different context, or the identifier is already in use.
        """
        AccessManager.require_workspace(actor, workspace_slug)
        async with Services.database.session() as session:
            existing = await Database.projects.get(id=data.id, session=session)
            if existing:
                if existing.workspace_slug != workspace_slug or existing.created_by != actor.id:
                    raise PmsError(409, "PROJECT_ID_TAKEN", "Project id is already in use.")
                access = await AccessManager.require_project(
                    session,
                    actor,
                    workspace_slug,
                    existing.id,
                )
                return project_api.ProjectResponse(
                    data=await cls._project_api(session, existing, access.role)
                )
            if await Database.projects.get(
                workspace_slug=workspace_slug,
                identifier=data.identifier,
                session=session,
            ):
                raise PmsError(409, "PROJECT_IDENTIFIER_TAKEN", "Project identifier is already in use.")
            icon = data.icon.model_dump() if data.icon else {
                "type": "initial",
                "value": data.name[0].upper(),
            }
            project = await Database.projects.upsert(
                data=pydantic.ProjectCreateDTO(
                    id=data.id,
                    workspace_slug=workspace_slug,
                    name=data.name,
                    identifier=data.identifier,
                    description=data.description,
                    icon=icon,
                    color=data.color.upper(),
                    access=data.access,
                    created_by=actor.id,
                ),
                conflict_fields={"workspace_slug", "identifier"},
                on_conflict="nothing",
                session=session,
                mode="json",
            )
            if project is None:
                raise PmsError(409, "PROJECT_IDENTIFIER_TAKEN", "Project identifier is already in use.")
            await Database.project_users.create(
                pydantic.ProjectUserCreateDTO(
                    project_id=project.id,
                    workspace_id=workspace_slug,
                    user_id=actor.id,
                    role=enum.ProjectRole.ADMIN,
                    source=enum.ProjectMembershipSource.BOOTSTRAP,
                ),
                session=session,
                mode="json",
            )
            states = await Database.states.bulk_create(
                [
                    pydantic.ProjectStateCreateDTO(
                        project_id=project.id,
                        name=name,
                        color=color,
                        group=group,
                        position=position,
                        is_default=is_default,
                    )
                    for position, (name, color, group, is_default) in enumerate(DEFAULT_STATES)
                ],
                session=session,
                mode="json",
            )
            default_state = next(state for state in states if state.is_default)
            project = await Database.projects.update(
                id=project.id,
                data=pydantic.ProjectUpdateFieldsDTO(default_state_id=default_state.id),
                session=session,
            )
            await AgentsManager.create_coordinator(
                session=session,
                project_id=project.id,
                created_by=actor.id,
            )
            result = project_api.ProjectResponse(
                data=await cls._project_api(session, project, enum.ProjectRole.ADMIN)
            )
            emit_event("project_created", project_id=project.id, workspace_slug=workspace_slug)
            return result

    @classmethod
    async def get_project(
        cls, workspace_slug: str, project_id: UUID, actor: pydantic.ActorDTO
    ) -> project_api.ProjectResponse:
        """Retrieve a project with actor-specific permissions and aggregates.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project to retrieve.
            actor: Request actor context.

        Returns:
            The enriched project response.

        Raises:
            PmsError: If the actor cannot access the project.
        """
        async with Services.database.session() as session:
            access = await AccessManager.require_project(session, actor, workspace_slug, project_id)
            return project_api.ProjectResponse(
                data=await cls._project_api(session, access.project, access.role)
            )

    @classmethod
    async def update_project(
        cls,
        workspace_slug: str,
        project_id: UUID,
        actor: pydantic.ActorDTO,
        data: project_api.UpdateProjectRequest,
    ) -> project_api.ProjectResponse:
        """Update mutable project fields and increment its version.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project to update.
            actor: Request actor context.
            data: Validated partial project fields.

        Returns:
            The current or updated enriched project.

        Raises:
            PmsError: If access is denied, the identifier is already used, or
                the project disappears during the update.
        """
        async with Services.database.session() as session:
            access = await AccessManager.require_project(
                session, actor, workspace_slug, project_id, "can_edit_project"
            )
            values = data.model_dump(exclude_unset=True)
            if not values:
                return project_api.ProjectResponse(
                    data=await cls._project_api(session, access.project, access.role)
                )
            if "icon" in values and values["icon"] is not None:
                values["icon"] = data.icon.model_dump()
            if "color" in values and values["color"]:
                values["color"] = values["color"].upper()
            if "identifier" in values:
                duplicate = await Database.projects.get(
                    workspace_slug=workspace_slug,
                    identifier=values["identifier"],
                    session=session,
                )
                if duplicate and duplicate.id != project_id:
                    raise PmsError(409, "PROJECT_IDENTIFIER_TAKEN", "Project identifier is already in use.")
            values["version"] = access.project.version + 1
            project = await Database.projects.update(
                id=project_id,
                data=pydantic.ProjectUpdateFieldsDTO(**values),
                workspace_slug=workspace_slug,
                session=session,
            )
            if not project:
                raise PmsError(404, "PROJECT_NOT_FOUND", "Project not found.")
            return project_api.ProjectResponse(
                data=await cls._project_api(session, project, access.role)
            )

    @classmethod
    async def archive_project(
        cls,
        workspace_slug: str,
        project_id: UUID,
        actor: pydantic.ActorDTO,
        data: project_api.ArchiveProjectRequest,
    ) -> project_api.ProjectResponse:
        """Archive a project after exact name confirmation.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project to archive.
            actor: Request actor context.
            data: Archive confirmation payload.

        Returns:
            The archived project, or the unchanged project if already archived.

        Raises:
            PmsError: If access is denied or the confirmation name differs.
        """
        async with Services.database.session() as session:
            access = await AccessManager.require_project(
                session, actor, workspace_slug, project_id
            )
            AccessManager.require_permission(access, "can_archive_project")
            if data.confirmation_name != access.project.name:
                raise PmsError(422, "VALIDATION_ERROR", "Project name confirmation does not match.")
            project = access.project
            if project.archived_at is None:
                project = await Database.projects.update(
                    id=project_id,
                    data=pydantic.ProjectUpdateFieldsDTO(
                        archived_at=datetime.now(timezone.utc),
                        version=project.version + 1,
                    ),
                    workspace_slug=workspace_slug,
                    session=session,
                )
            result = project_api.ProjectResponse(
                data=await cls._project_api(session, project, access.role)
            )
            if access.project.archived_at is None:
                emit_event("project_archived", project_id=project_id, workspace_slug=workspace_slug)
            return result

    @classmethod
    async def restore_project(
        cls,
        workspace_slug: str,
        project_id: UUID,
        actor: pydantic.ActorDTO,
    ) -> project_api.ProjectResponse:
        """Restore an archived project.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project to restore.
            actor: Request actor context.

        Returns:
            The active project, or the unchanged project if already active.

        Raises:
            PmsError: If the actor lacks project archive permission.
        """
        async with Services.database.session() as session:
            access = await AccessManager.require_project(
                session, actor, workspace_slug, project_id
            )
            AccessManager.require_permission(access, "can_archive_project")
            project = access.project
            if project.archived_at is not None:
                project = await Database.projects.update(
                    id=project_id,
                    data=pydantic.ProjectUpdateFieldsDTO(
                        archived_at=None,
                        version=project.version + 1,
                    ),
                    workspace_slug=workspace_slug,
                    session=session,
                )
            result = project_api.ProjectResponse(
                data=await cls._project_api(session, project, access.role)
            )
            return result
