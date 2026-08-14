from uuid import UUID

from api.db.db import Database
from api.managers.common import (
    AccessManager,
    PmsError,
    cursor_meta,
    decode_cursor,
    emit_event,
    member_summaries,
    parse_enum_csv,
    parse_uuid_csv,
    sanitize_html,
)
from api.managers.states import StatesManager
from api.managers.work_items import WorkItemsManager
from api.services import Services
from models import enum, pydantic
from models.pydantic.api import epic_api, work_item_api


class EpicsManager:
    """Manage epics, assignees, progress views, and work-item membership."""

    @staticmethod
    async def _assignee_map(
        session,
        epic_ids: list[UUID],
    ) -> dict[UUID, list[UUID]]:
        """Map epic identifiers to their ordered assignee identifiers."""

        mapped = {epic_id: [] for epic_id in epic_ids}
        if not epic_ids:
            return mapped
        assignees = await Database.epic_assignees.get_list(
            epic_id=epic_ids,
            sort_by="user_id",
            session=session,
        )
        for assignee in assignees:
            mapped[assignee.epic_id].append(assignee.user_id)
        return mapped

    @staticmethod
    async def _replace_assignees(
        session,
        epic_id: UUID,
        user_ids: list[UUID],
    ) -> None:
        """Replace every assignee relation for an epic.

        Args:
            session: Active database session.
            epic_id: Epic whose assignees are replaced.
            user_ids: New assignee identifiers in requested order.
        """
        await Database.epic_assignees.delete_list(
            epic_id=epic_id,
            session=session,
        )
        await Database.epic_assignees.bulk_create(
            [
                pydantic.EpicAssigneeCreateDTO(
                    epic_id=epic_id,
                    user_id=user_id,
                )
                for user_id in user_ids
            ],
            session=session,
        )

    @staticmethod
    def _list_item(
        epic: pydantic.EpicDTO,
        project_identifier: str,
        assignee_ids: list[UUID],
        work_items_count: int,
        completed_work_items_count: int,
        progress_percent: int,
    ) -> epic_api.EpicListItem:
        """Build an epic list item from persisted and aggregate values."""

        return epic_api.EpicListItem(
            id=epic.id,
            project_id=epic.project_id,
            sequence_id=epic.sequence_id,
            identifier=f"{project_identifier}-E{epic.sequence_id}",
            title=epic.title,
            state_id=epic.state_id,
            priority=epic.priority,
            assignee_ids=assignee_ids,
            start_date=epic.start_date,
            due_date=epic.due_date,
            rank=epic.rank,
            work_items_count=work_items_count,
            completed_work_items_count=completed_work_items_count,
            progress_percent=progress_percent,
            created_by=epic.created_by,
            created_at=epic.created_at,
            updated_at=epic.updated_at,
            version=epic.version,
        )

    @classmethod
    async def _full(cls, session, epic: pydantic.EpicDTO, project_identifier: str) -> epic_api.Epic:
        """Build a complete epic representation with assignees and progress.

        Args:
            session: Active database session.
            epic: Epic DTO to expose.
            project_identifier: Prefix used for the display identifier.

        Returns:
            The complete epic API model.

        Raises:
            PmsError: If the epic no longer exists while loading progress.
        """
        assignees = await cls._assignee_map(session, [epic.id])
        progress_row = await Database.epics.get_with_progress(
            session,
            epic.project_id,
            epic.id,
        )
        if progress_row is None:
            raise PmsError(404, "EPIC_NOT_FOUND", "Epic not found.")
        item = cls._list_item(
            epic,
            project_identifier,
            assignees.get(epic.id, []),
            int(progress_row.work_items_count),
            int(progress_row.completed_work_items_count),
            int(progress_row.progress_percent),
        )
        return epic_api.Epic(**item.model_dump(), description_html=epic.description_html)

    @staticmethod
    async def _validate_references(
        session, project_id: UUID, state_id: UUID, assignee_ids: list[UUID]
    ) -> None:
        """Validate an epic's state and assignees against its project.

        Args:
            session: Active database session.
            project_id: Project that must own all references.
            state_id: Workflow state to validate.
            assignee_ids: Project members to validate.

        Raises:
            PmsError: If the state or any assignee is outside the project.
        """
        state = await Database.states.get(id=state_id, project_id=project_id, session=session)
        if not state:
            raise PmsError(422, "CROSS_PROJECT_REFERENCE", "State does not belong to this project.")
        await AccessManager.validate_members(session, project_id, assignee_ids)

    @classmethod
    async def list_epics(
        cls,
        workspace_slug: str,
        project_id: UUID,
        actor: pydantic.ActorDTO,
        queries: epic_api.EpicListQueries,
    ) -> epic_api.EpicPage:
        """List filtered epics with progress and cursor metadata.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project whose epics are requested.
            actor: Request actor context.
            queries: Search, filter, sort, and cursor options.

        Returns:
            A cursor-paginated page of epic list items.

        Raises:
            PmsError: If filters are malformed or project access fails.
        """
        offset = decode_cursor(queries.cursor)
        state_groups = parse_enum_csv(queries.state_group, enum.StateGroup, "state_group")
        priorities = parse_enum_csv(queries.priority, enum.Priority, "priority")
        assignee_ids = parse_uuid_csv(queries.assignee_id, "assignee_id")
        async with Services.database.session() as session:
            access = await AccessManager.require_project(session, actor, workspace_slug, project_id)
            rows, total = await Database.epics.list_with_progress(
                session=session,
                project_id=project_id,
                search=queries.search,
                state_groups=state_groups,
                priorities=priorities,
                assignee_ids=assignee_ids,
                status=queries.status,
                sort=queries.sort,
                offset=offset,
                limit=queries.limit,
            )
            epic_ids = [pydantic.EpicDTO.model_validate(row).id for row in rows]
            assignees = await cls._assignee_map(session, epic_ids)
            items = []
            for row in rows:
                epic = pydantic.EpicDTO.model_validate(row)
                items.append(
                    cls._list_item(
                        epic,
                        access.project.identifier,
                        assignees.get(epic.id, []),
                        int(row.work_items_count),
                        int(row.completed_work_items_count),
                        int(row.progress_percent),
                    )
                )
            return epic_api.EpicPage(
                data=items,
                meta=cursor_meta(offset, queries.limit, len(items), total),
            )

    @classmethod
    async def create_epic(
        cls,
        workspace_slug: str,
        project_id: UUID,
        actor: pydantic.ActorDTO,
        data: epic_api.CreateEpicRequest,
    ) -> epic_api.EpicResponse:
        """Create an idempotent epic with validated references and safe HTML.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project receiving the epic.
            actor: Request actor context.
            data: Validated epic creation fields.

        Returns:
            The existing idempotent result or newly created epic.

        Raises:
            PmsError: If access, reference, default-state, or HTML validation
                fails, or the supplied ID belongs to another project.
        """
        async with Services.database.session() as session:
            access = await AccessManager.require_project(
                session, actor, workspace_slug, project_id, "can_create_epic"
            )
            existing = await Database.epics.get(id=data.id, session=session)
            if existing:
                if existing.project_id != project_id:
                    raise PmsError(
                        422,
                        "CROSS_PROJECT_REFERENCE",
                        "Epic id belongs to another project.",
                    )
                return epic_api.EpicResponse(
                    data=await cls._full(session, existing, access.project.identifier)
                )
            project = access.project
            state_id = data.state_id or project.default_state_id
            if state_id is None:
                raise PmsError(500, "INTERNAL_ERROR", "Project has no default state.")
            assignee_ids = data.assignee_ids or []
            await cls._validate_references(session, project_id, state_id, assignee_ids)
            sequence_id = await Database.projects.allocate_sequence(
                session, project_id, "next_epic_sequence"
            )
            epic = await Database.epics.create(
                pydantic.EpicCreateDTO(
                    id=data.id,
                    project_id=project_id,
                    sequence_id=sequence_id,
                    title=data.title,
                    description_html=sanitize_html(data.description_html or ""),
                    state_id=state_id,
                    priority=data.priority or enum.Priority.NONE,
                    start_date=data.start_date,
                    due_date=data.due_date,
                    rank=await Database.epics.next_rank(session, project_id),
                    created_by=actor.id,
                ),
                session=session,
                mode="json",
            )
            await cls._replace_assignees(session, epic.id, assignee_ids)
            result = epic_api.EpicResponse(
                data=await cls._full(session, epic, access.project.identifier)
            )
            emit_event("epic_created", project_id=project_id, epic_id=epic.id)
            return result

    @classmethod
    async def get_epic(
        cls,
        workspace_slug: str,
        project_id: UUID,
        epic_id: UUID,
        actor: pydantic.ActorDTO,
    ) -> epic_api.EpicDetailResponse:
        """Retrieve an epic with states, members, and actor permissions.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project expected to own the epic.
            epic_id: Epic to retrieve.
            actor: Request actor context.

        Returns:
            Detailed epic data and related lookup entities.

        Raises:
            PmsError: If access fails or the epic is missing.
        """
        async with Services.database.session() as session:
            access = await AccessManager.require_project(session, actor, workspace_slug, project_id)
            epic = await Database.epics.get(id=epic_id, project_id=project_id, session=session)
            if not epic:
                raise PmsError(404, "EPIC_NOT_FOUND", "Epic not found.")
            return epic_api.EpicDetailResponse(
                data=epic_api.EpicDetailData(
                    epic=await cls._full(session, epic, access.project.identifier),
                    included=epic_api.EpicIncluded(
                        states=await StatesManager._list(session, project_id),
                        members=await member_summaries(session, project_id),
                    ),
                    permissions=access.permissions,
                )
            )

    @classmethod
    async def update_epic(
        cls,
        workspace_slug: str,
        project_id: UUID,
        epic_id: UUID,
        actor: pydantic.ActorDTO,
        data: epic_api.UpdateEpicRequest,
    ) -> epic_api.EpicResponse:
        """Update epic fields, references, assignees, and sanitized HTML.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project expected to own the epic.
            epic_id: Epic to update.
            actor: Request actor context.
            data: Validated partial epic fields.

        Returns:
            The current or updated complete epic.

        Raises:
            PmsError: If access fails, the epic is missing, references are
                invalid, dates are inconsistent, or description HTML is null or
                oversized after sanitization.
        """
        async with Services.database.session() as session:
            access = await AccessManager.require_project(
                session, actor, workspace_slug, project_id, "can_edit_epic"
            )
            current = await Database.epics.get(
                id=epic_id,
                project_id=project_id,
                session=session,
            )
            if not current:
                raise PmsError(404, "EPIC_NOT_FOUND", "Epic not found.")
            values = data.model_dump(exclude_unset=True)
            if not values:
                return epic_api.EpicResponse(
                    data=await cls._full(session, current, access.project.identifier)
                )
            assignee_ids = values.pop("assignee_ids", None)
            state_id = values.get("state_id", current.state_id)
            final_assignees = assignee_ids
            if final_assignees is None:
                final_assignees = (await cls._assignee_map(session, [epic_id])).get(epic_id, [])
            await cls._validate_references(session, project_id, state_id, final_assignees)
            start_date = values.get("start_date", current.start_date)
            due_date = values.get("due_date", current.due_date)
            if start_date and due_date and start_date > due_date:
                raise PmsError(422, "VALIDATION_ERROR", "start_date must be before or equal to due_date.")
            if "description_html" in values:
                if values["description_html"] is None:
                    raise PmsError(422, "VALIDATION_ERROR", "description_html cannot be null.")
                values["description_html"] = sanitize_html(values["description_html"])
            values["version"] = current.version + 1
            epic = await Database.epics.update(
                id=epic_id,
                data=pydantic.EpicUpdateFieldsDTO(**values),
                project_id=project_id,
                session=session,
            )
            if not epic:
                raise PmsError(404, "EPIC_NOT_FOUND", "Epic not found.")
            if assignee_ids is not None:
                await cls._replace_assignees(session, epic.id, assignee_ids)
            return epic_api.EpicResponse(
                data=await cls._full(session, epic, access.project.identifier)
            )

    @classmethod
    async def delete_epic(
        cls,
        workspace_slug: str,
        project_id: UUID,
        epic_id: UUID,
        actor: pydantic.ActorDTO,
    ) -> None:
        """Delete an epic and detach its linked work items.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project expected to own the epic.
            epic_id: Epic to delete.
            actor: Request actor context.

        Raises:
            PmsError: If the epic is missing or the actor lacks deletion rights.
        """
        async with Services.database.session() as session:
            access = await AccessManager.require_project(session, actor, workspace_slug, project_id)
            epic = await Database.epics.get(
                id=epic_id,
                project_id=project_id,
                session=session,
            )
            if not epic:
                raise PmsError(404, "EPIC_NOT_FOUND", "Epic not found.")
            can_delete = access.permissions.can_delete_any_epic or (
                epic.created_by == actor.id and access.permissions.can_delete_own_epic
            )
            if not can_delete or access.project.archived_at is not None:
                raise PmsError(403, "FORBIDDEN", "Permission denied.")
            linked = await Database.work_items.get_list(epic_id=epic_id, project_id=project_id, session=session)
            await Database.work_items.set_epic(
                session,
                project_id,
                [item.id for item in linked],
                None,
            )
            await Database.epics.delete(epic_id, project_id=project_id, session=session)

    @classmethod
    async def list_epic_work_items(
        cls,
        workspace_slug: str,
        project_id: UUID,
        epic_id: UUID,
        actor: pydantic.ActorDTO,
        search: str | None,
        cursor: str | None,
        limit: int,
    ) -> work_item_api.WorkItemPage:
        """List work items currently linked to an epic.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project expected to own the epic.
            epic_id: Epic whose work items are requested.
            actor: Request actor context.
            search: Optional work-item search text.
            cursor: Optional pagination cursor.
            limit: Maximum work items to return.

        Returns:
            A cursor-paginated page of work-item cards.

        Raises:
            PmsError: If the cursor or access is invalid or the epic is missing.
        """
        offset = decode_cursor(cursor)
        async with Services.database.session() as session:
            access = await AccessManager.require_project(session, actor, workspace_slug, project_id)
            if not await Database.epics.get(id=epic_id, project_id=project_id, session=session):
                raise PmsError(404, "EPIC_NOT_FOUND", "Epic not found.")
            items, total = await Database.work_items.list_filtered(
                session=session,
                project_id=project_id,
                search=search,
                epic_id=epic_id,
                offset=offset,
                limit=limit,
            )
            assignees = await WorkItemsManager._assignee_map(
                session, [item.id for item in items]
            )
            cards = [
                WorkItemsManager._card(item, access.project.identifier, assignees.get(item.id, []))
                for item in items
            ]
            return work_item_api.WorkItemPage(
                data=cards, meta=cursor_meta(offset, limit, len(cards), total)
            )

    @classmethod
    async def add_work_items(
        cls,
        workspace_slug: str,
        project_id: UUID,
        epic_id: UUID,
        actor: pydantic.ActorDTO,
        data: epic_api.AddEpicWorkItemsRequest,
    ) -> epic_api.EpicWorkItemsMutationResponse:
        """Attach work items to an epic, optionally moving them from others.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project expected to own all entities.
            epic_id: Epic receiving the work items.
            actor: Request actor context.
            data: Work-item identifiers and move policy.

        Returns:
            The refreshed epic summary and updated work-item cards.

        Raises:
            PmsError: If access fails, IDs are duplicated or cross-project, the
                epic is missing, or moving from another epic is disallowed.
        """
        async with Services.database.session() as session:
            access = await AccessManager.require_project(
                session, actor, workspace_slug, project_id, "can_edit_epic"
            )
            epic = await Database.epics.get(
                id=epic_id,
                project_id=project_id,
                session=session,
            )
            if not epic:
                raise PmsError(404, "EPIC_NOT_FOUND", "Epic not found.")
            if len(set(data.work_item_ids)) != len(data.work_item_ids):
                raise PmsError(422, "VALIDATION_ERROR", "work_item_ids must be unique.")
            items = await Database.work_items.get_by_ids(data.work_item_ids, project_id=project_id, session=session)
            if {item.id for item in items} != set(data.work_item_ids):
                raise PmsError(422, "CROSS_PROJECT_REFERENCE", "Work item does not belong to this project.")
            if not data.move_from_other_epics and any(
                item.epic_id not in {None, epic_id} for item in items
            ):
                raise PmsError(
                    409,
                    "WORK_ITEM_ALREADY_IN_EPIC",
                    "A work item already belongs to another epic.",
                )
            changed = await Database.work_items.set_epic(
                session,
                project_id,
                [item.id for item in items if item.epic_id != epic_id],
                epic_id,
            )
            item_map = {item.id: item for item in items}
            item_map.update({item.id: item for item in changed})
            updated = [item_map[item_id] for item_id in data.work_item_ids]
            assignees = await WorkItemsManager._assignee_map(
                session, [item.id for item in updated]
            )
            cards = [
                WorkItemsManager._card(item, access.project.identifier, assignees.get(item.id, []))
                for item in updated
            ]
            full_epic = await cls._full(session, epic, access.project.identifier)
            list_item = epic_api.EpicListItem.model_validate(
                full_epic.model_dump(exclude={"description_html"})
            )
            result = epic_api.EpicWorkItemsMutationResponse(
                data=epic_api.EpicWorkItemsMutationData(
                    epic=list_item, updated_work_items=cards
                )
            )
            emit_event("epic_work_items_changed", project_id=project_id, epic_id=epic_id)
            return result

    @classmethod
    async def remove_work_item(
        cls,
        workspace_slug: str,
        project_id: UUID,
        epic_id: UUID,
        work_item_id: UUID,
        actor: pydantic.ActorDTO,
    ) -> epic_api.EpicWorkItemsMutationResponse:
        """Detach one work item from an epic.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project expected to own both entities.
            epic_id: Epic losing the work item.
            work_item_id: Work item to detach.
            actor: Request actor context.

        Returns:
            The refreshed epic summary and detached work-item card.

        Raises:
            PmsError: If access fails, either entity is missing, or the item is
                not linked to the specified epic.
        """
        async with Services.database.session() as session:
            access = await AccessManager.require_project(
                session, actor, workspace_slug, project_id, "can_edit_epic"
            )
            epic = await Database.epics.get(
                id=epic_id,
                project_id=project_id,
                session=session,
            )
            if not epic:
                raise PmsError(404, "EPIC_NOT_FOUND", "Epic not found.")
            item = await Database.work_items.get(
                id=work_item_id,
                project_id=project_id,
                session=session,
            )
            if not item:
                raise PmsError(404, "WORK_ITEM_NOT_FOUND", "Work item not found.")
            if item.epic_id != epic_id:
                raise PmsError(422, "CROSS_PROJECT_REFERENCE", "Work item is not linked to this epic.")
            item = (
                await Database.work_items.set_epic(
                    session,
                    project_id,
                    [item.id],
                    None,
                )
            )[0]
            assignees = await WorkItemsManager._assignee_map(session, [item.id])
            full_epic = await cls._full(session, epic, access.project.identifier)
            result = epic_api.EpicWorkItemsMutationResponse(
                data=epic_api.EpicWorkItemsMutationData(
                    epic=epic_api.EpicListItem.model_validate(
                        full_epic.model_dump(exclude={"description_html"})
                    ),
                    updated_work_items=[
                        WorkItemsManager._card(
                            item, access.project.identifier, assignees.get(item.id, [])
                        )
                    ],
                )
            )
            emit_event("epic_work_items_changed", project_id=project_id, epic_id=epic_id)
            return result
