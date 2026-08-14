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
from api.services import Services
from models import enum, pydantic
from models.pydantic.api import epic_api, work_item_api


class WorkItemsManager:
    """Manage work items, assignees, ordering, and detailed read models."""

    @staticmethod
    async def _assignee_map(
        session,
        work_item_ids: list[UUID],
    ) -> dict[UUID, list[UUID]]:
        """Map work-item identifiers to their ordered assignee identifiers."""

        mapped = {work_item_id: [] for work_item_id in work_item_ids}
        if not work_item_ids:
            return mapped
        assignees = await Database.work_item_assignees.get_list(
            work_item_id=work_item_ids,
            sort_by="user_id",
            session=session,
        )
        for assignee in assignees:
            mapped[assignee.work_item_id].append(assignee.user_id)
        return mapped

    @staticmethod
    async def _replace_assignees(
        session,
        work_item_id: UUID,
        user_ids: list[UUID],
    ) -> None:
        """Replace every assignee relation for a work item.

        Args:
            session: Active database session.
            work_item_id: Work item whose assignees are replaced.
            user_ids: New assignee identifiers in requested order.
        """
        await Database.work_item_assignees.delete_list(
            work_item_id=work_item_id,
            session=session,
        )
        await Database.work_item_assignees.bulk_create(
            [
                pydantic.WorkItemAssigneeCreateDTO(
                    work_item_id=work_item_id,
                    user_id=user_id,
                )
                for user_id in user_ids
            ],
            session=session,
        )

    @staticmethod
    def _card(
        item: pydantic.WorkItemDTO,
        project_identifier: str,
        assignee_ids: list[UUID],
    ) -> work_item_api.WorkItemCard:
        """Build a board-card representation from a work-item DTO."""

        return work_item_api.WorkItemCard(
            id=item.id,
            project_id=item.project_id,
            sequence_id=item.sequence_id,
            identifier=f"{project_identifier}-{item.sequence_id}",
            title=item.title,
            state_id=item.state_id,
            priority=item.priority,
            assignee_ids=assignee_ids,
            epic_id=item.epic_id,
            start_date=item.start_date,
            due_date=item.due_date,
            rank=item.rank,
            created_by=item.created_by,
            created_at=item.created_at,
            updated_at=item.updated_at,
            version=item.version,
        )

    @classmethod
    async def _full(
        cls, session, item: pydantic.WorkItemDTO, project_identifier: str
    ) -> work_item_api.WorkItem:
        """Build a complete work-item representation with assignees."""

        assignees = await cls._assignee_map(session, [item.id])
        card = cls._card(item, project_identifier, assignees.get(item.id, []))
        return work_item_api.WorkItem(**card.model_dump(), description_html=item.description_html)

    @staticmethod
    async def _validate_references(
        session,
        project_id: UUID,
        state_id: UUID,
        epic_id: UUID | None,
        assignee_ids: list[UUID],
    ) -> None:
        """Validate state, epic, and assignee references within a project.

        Args:
            session: Active database session.
            project_id: Project that must own all references.
            state_id: Workflow state to validate.
            epic_id: Optional epic to validate.
            assignee_ids: Project members to validate.

        Raises:
            PmsError: If any reference falls outside the project.
        """
        state = await Database.states.get(id=state_id, project_id=project_id, session=session)
        if not state:
            raise PmsError(422, "CROSS_PROJECT_REFERENCE", "State does not belong to this project.")
        if epic_id:
            epic = await Database.epics.get(id=epic_id, project_id=project_id, session=session)
            if not epic:
                raise PmsError(422, "CROSS_PROJECT_REFERENCE", "Epic does not belong to this project.")
        await AccessManager.validate_members(session, project_id, assignee_ids)

    @classmethod
    async def list_work_items(
        cls,
        workspace_slug: str,
        project_id: UUID,
        actor: pydantic.ActorDTO,
        queries: work_item_api.WorkItemListQueries,
    ) -> work_item_api.WorkItemPage:
        """List filtered work-item cards with cursor metadata.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project whose work items are requested.
            actor: Request actor context.
            queries: Search, filter, sort, and cursor options.

        Returns:
            A cursor-paginated page of work-item cards.

        Raises:
            PmsError: If filters are malformed or project access fails.
        """
        offset = decode_cursor(queries.cursor)
        priorities = parse_enum_csv(queries.priority, enum.Priority, "priority")
        assignee_ids = parse_uuid_csv(queries.assignee_id, "assignee_id")
        epic_id: UUID | str | None = queries.epic_id
        if epic_id and epic_id != "none":
            try:
                epic_id = UUID(epic_id)
            except ValueError as exc:
                raise PmsError(400, "MALFORMED_REQUEST", "Invalid epic_id filter.") from exc
        async with Services.database.session() as session:
            access = await AccessManager.require_project(session, actor, workspace_slug, project_id)
            items, total = await Database.work_items.list_filtered(
                session=session,
                project_id=project_id,
                search=queries.search,
                state_id=queries.state_id,
                priorities=priorities,
                assignee_ids=assignee_ids,
                epic_id=epic_id,
                due_status=queries.due_status,
                created_by=queries.created_by,
                sort=queries.sort,
                offset=offset,
                limit=queries.limit,
            )
            mapped = await cls._assignee_map(session, [item.id for item in items])
            cards = [
                cls._card(item, access.project.identifier, mapped.get(item.id, [])) for item in items
            ]
            return work_item_api.WorkItemPage(
                data=cards,
                meta=cursor_meta(offset, queries.limit, len(cards), total),
            )

    @classmethod
    async def create_work_item(
        cls,
        workspace_slug: str,
        project_id: UUID,
        actor: pydantic.ActorDTO,
        data: work_item_api.CreateWorkItemRequest,
    ) -> work_item_api.WorkItemResponse:
        """Create an idempotent work item with validated references and rank.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project receiving the work item.
            actor: Request actor context.
            data: Validated work-item creation fields and optional anchors.

        Returns:
            The existing idempotent result or newly created work item, with
            board version metadata for new records.

        Raises:
            PmsError: If access, references, position, default-state, or HTML
                validation fails, or the supplied ID belongs to another project.
        """
        async with Services.database.session() as session:
            access = await AccessManager.require_project(
                session, actor, workspace_slug, project_id, "can_create_work_item"
            )
            existing = await Database.work_items.get(id=data.id, session=session)
            if existing:
                if existing.project_id != project_id:
                    raise PmsError(
                        422,
                        "CROSS_PROJECT_REFERENCE",
                        "Work item id belongs to another project.",
                    )
                return work_item_api.WorkItemResponse(
                    data=await cls._full(session, existing, access.project.identifier)
                )
            project = access.project
            state_id = data.state_id or project.default_state_id
            if state_id is None:
                raise PmsError(500, "INTERNAL_ERROR", "Project has no default state.")
            assignee_ids = data.assignee_ids or []
            await cls._validate_references(session, project_id, state_id, data.epic_id, assignee_ids)
            try:
                rank, _, _ = await Database.work_items.allocate_rank(
                    session,
                    project_id,
                    state_id,
                    data.before_work_item_id,
                    data.after_work_item_id,
                )
            except ValueError as exc:
                raise PmsError(422, "INVALID_POSITION", str(exc)) from exc
            sequence_id = await Database.projects.allocate_sequence(
                session, project_id, "next_work_item_sequence"
            )
            description = sanitize_html(data.description_html or "")
            item = await Database.work_items.create(
                pydantic.WorkItemCreateDTO(
                    id=data.id,
                    project_id=project_id,
                    sequence_id=sequence_id,
                    title=data.title,
                    description_html=description,
                    state_id=state_id,
                    priority=data.priority or enum.Priority.NONE,
                    epic_id=data.epic_id,
                    start_date=data.start_date,
                    due_date=data.due_date,
                    rank=rank,
                    created_by=actor.id,
                ),
                session=session,
                mode="json",
            )
            await cls._replace_assignees(session, item.id, assignee_ids)
            board_version = await Database.projects.increment_board_version(session, project_id)
            result = work_item_api.WorkItemResponse(
                data=await cls._full(session, item, access.project.identifier),
                meta={"board_version": board_version},
            )
            emit_event("work_item_created", project_id=project_id, work_item_id=item.id)
            return result

    @classmethod
    async def get_work_item(
        cls,
        workspace_slug: str,
        project_id: UUID,
        work_item_id: UUID,
        actor: pydantic.ActorDTO,
    ) -> work_item_api.WorkItemDetailResponse:
        """Retrieve a work item with related states, members, and epics.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project expected to own the work item.
            work_item_id: Work item to retrieve.
            actor: Request actor context.

        Returns:
            Detailed work-item data, lookup entities, and actor permissions.

        Raises:
            PmsError: If access fails or the work item is missing.
        """
        async with Services.database.session() as session:
            access = await AccessManager.require_project(session, actor, workspace_slug, project_id)
            item = await Database.work_items.get(
                id=work_item_id, project_id=project_id, session=session
            )
            if not item:
                raise PmsError(404, "WORK_ITEM_NOT_FOUND", "Work item not found.")
            emit_event("work_item_opened", project_id=project_id, work_item_id=work_item_id)
            epic_rows, _ = await Database.epics.list_with_progress(
                session, project_id, limit=100
            )
            epics = []
            for row in epic_rows:
                epic = pydantic.EpicDTO.model_validate(row)
                epics.append(
                    epic_api.EpicPickerItem(
                        id=epic.id,
                        identifier=f"{access.project.identifier}-E{epic.sequence_id}",
                        title=epic.title,
                        state_id=epic.state_id,
                        progress_percent=int(row.progress_percent),
                    )
                )
            return work_item_api.WorkItemDetailResponse(
                data=work_item_api.WorkItemDetailData(
                    work_item=await cls._full(session, item, access.project.identifier),
                    included=work_item_api.WorkItemIncluded(
                        states=await StatesManager._list(session, project_id),
                        members=await member_summaries(session, project_id),
                        epics=epics,
                    ),
                    permissions=access.permissions,
                )
            )

    @classmethod
    async def update_work_item(
        cls,
        workspace_slug: str,
        project_id: UUID,
        work_item_id: UUID,
        actor: pydantic.ActorDTO,
        data: work_item_api.UpdateWorkItemRequest,
    ) -> work_item_api.WorkItemResponse:
        """Update work-item fields, references, assignees, and safe HTML.

        Moving to a different state also allocates a new rank and increments the
        project board version.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project expected to own the work item.
            work_item_id: Work item to update.
            actor: Request actor context.
            data: Validated partial work-item fields.

        Returns:
            The current or updated work item and optional board metadata.

        Raises:
            PmsError: If access fails, the item is missing, references or dates
                are invalid, or description HTML is null or oversized.
        """
        async with Services.database.session() as session:
            access = await AccessManager.require_project(
                session, actor, workspace_slug, project_id, "can_edit_work_item"
            )
            current = await Database.work_items.get(
                id=work_item_id,
                project_id=project_id,
                session=session,
            )
            if not current:
                raise PmsError(404, "WORK_ITEM_NOT_FOUND", "Work item not found.")
            values = data.model_dump(exclude_unset=True)
            if not values:
                return work_item_api.WorkItemResponse(
                    data=await cls._full(session, current, access.project.identifier)
                )
            assignee_ids = values.pop("assignee_ids", None)
            state_id = values.get("state_id", current.state_id)
            epic_id = values.get("epic_id", current.epic_id)
            final_assignees = assignee_ids
            if final_assignees is None:
                assignee_map = await cls._assignee_map(
                    session, [work_item_id]
                )
                final_assignees = assignee_map.get(work_item_id, [])
            await cls._validate_references(session, project_id, state_id, epic_id, final_assignees)
            start_date = values.get("start_date", current.start_date)
            due_date = values.get("due_date", current.due_date)
            if start_date and due_date and start_date > due_date:
                raise PmsError(422, "VALIDATION_ERROR", "start_date must be before or equal to due_date.")
            if "description_html" in values:
                if values["description_html"] is None:
                    raise PmsError(422, "VALIDATION_ERROR", "description_html cannot be null.")
                values["description_html"] = sanitize_html(values["description_html"])
            structural = state_id != current.state_id
            if structural:
                rank, _, _ = await Database.work_items.allocate_rank(
                    session, project_id, state_id, None, None, current.id
                )
                values["rank"] = rank
            values["version"] = current.version + 1
            item = await Database.work_items.update(
                id=work_item_id,
                data=pydantic.WorkItemUpdateFieldsDTO(**values),
                project_id=project_id,
                session=session,
            )
            if not item:
                raise PmsError(404, "WORK_ITEM_NOT_FOUND", "Work item not found.")
            if assignee_ids is not None:
                await cls._replace_assignees(session, item.id, assignee_ids)
            meta = None
            if structural:
                meta = {"board_version": await Database.projects.increment_board_version(session, project_id)}
            return work_item_api.WorkItemResponse(
                data=await cls._full(session, item, access.project.identifier), meta=meta
            )

    @classmethod
    async def move_work_item(
        cls,
        workspace_slug: str,
        project_id: UUID,
        work_item_id: UUID,
        actor: pydantic.ActorDTO,
        data: work_item_api.MoveWorkItemRequest,
    ) -> work_item_api.MoveWorkItemResponse:
        """Move a work item under board and item optimistic concurrency.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project expected to own the work item and target state.
            work_item_id: Work item to move.
            actor: Request actor context.
            data: Target state, ordering anchors, expected versions, and client
                mutation identifier.

        Returns:
            The moved card, new board version, canonical neighbors, and echoed
            client mutation identifier.

        Raises:
            PmsError: If access fails, either version is stale, the item or
                target state is missing, or the requested position is invalid.
        """
        async with Services.database.session() as session:
            access = await AccessManager.require_project(
                session, actor, workspace_slug, project_id, "can_move_work_item"
            )
            project = access.project
            if project.board_version != data.expected_board_version:
                raise PmsError(
                    409,
                    "BOARD_VERSION_CONFLICT",
                    "Board version is stale.",
                    details={"board_version": project.board_version},
                )
            item = await Database.work_items.get(
                id=work_item_id,
                project_id=project_id,
                session=session,
            )
            if not item:
                raise PmsError(404, "WORK_ITEM_NOT_FOUND", "Work item not found.")
            if item.version != data.expected_work_item_version:
                raise PmsError(409, "WORK_ITEM_VERSION_CONFLICT", "Work item version is stale.")
            target = await Database.states.get(
                id=data.to_state_id, project_id=project_id, session=session
            )
            if not target:
                raise PmsError(422, "TARGET_STATE_NOT_FOUND", "Target state not found.")
            try:
                rank, canonical_after, canonical_before = await Database.work_items.allocate_rank(
                    session,
                    project_id,
                    data.to_state_id,
                    data.before_work_item_id,
                    data.after_work_item_id,
                    item.id,
                )
            except ValueError as exc:
                raise PmsError(422, "INVALID_POSITION", str(exc)) from exc
            item = await Database.work_items.update(
                id=item.id,
                data=pydantic.WorkItemUpdateFieldsDTO(
                    state_id=data.to_state_id,
                    rank=rank,
                    version=item.version + 1,
                ),
                project_id=project_id,
                session=session,
            )
            board_version = await Database.projects.increment_board_version(session, project_id)
            assignees = await cls._assignee_map(session, [item.id])
            result = work_item_api.MoveWorkItemResponse(
                data=work_item_api.MoveWorkItemData(
                    work_item=cls._card(item, access.project.identifier, assignees.get(item.id, [])),
                    board_version=board_version,
                    client_mutation_id=data.client_mutation_id,
                    canonical_before_work_item_id=canonical_before,
                    canonical_after_work_item_id=canonical_after,
                )
            )
            emit_event(
                "work_item_moved",
                project_id=project_id,
                work_item_id=work_item_id,
                board_version=board_version,
            )
            return result

    @classmethod
    async def delete_work_item(
        cls,
        workspace_slug: str,
        project_id: UUID,
        work_item_id: UUID,
        actor: pydantic.ActorDTO,
    ) -> None:
        """Delete a work item and advance the project board version.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project expected to own the work item.
            work_item_id: Work item to delete.
            actor: Request actor context.

        Raises:
            PmsError: If the item is missing, the project is archived, or the
                actor lacks the applicable deletion permission.
        """
        async with Services.database.session() as session:
            access = await AccessManager.require_project(session, actor, workspace_slug, project_id)
            item = await Database.work_items.get(
                id=work_item_id,
                project_id=project_id,
                session=session,
            )
            if not item:
                raise PmsError(404, "WORK_ITEM_NOT_FOUND", "Work item not found.")
            can_delete = access.permissions.can_delete_any_work_item or (
                item.created_by == actor.id and access.permissions.can_delete_own_work_item
            )
            if not can_delete or access.project.archived_at is not None:
                raise PmsError(403, "FORBIDDEN", "Permission denied.")
            await Database.work_items.delete(item.id, project_id=project_id, session=session)
            await Database.projects.increment_board_version(session, project_id)
