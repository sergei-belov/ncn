from uuid import UUID

from api.db.db import Database
from api.managers.common import (
    DEFAULT_DISPLAY,
    AccessManager,
    PmsError,
    encode_cursor,
    emit_event,
    member_summaries,
    parse_enum_csv,
    parse_uuid_csv,
)
from api.managers.projects import ProjectsManager
from api.managers.states import StatesManager
from api.managers.work_items import WorkItemsManager
from api.services import Services
from models import enum, pydantic
from models.pydantic.api import board_api, common_api, epic_api


class BoardManager:
    """Assemble project board read models and manage user preferences."""

    @staticmethod
    async def _preferences(session, project_id: UUID, actor_id: UUID) -> pydantic.BoardPreferenceDTO:
        """Load or lazily initialize a user's board preferences.

        Args:
            session: Active database session.
            project_id: Project whose board preferences are requested.
            actor_id: User who owns the preferences.

        Returns:
            Existing or newly initialized board preferences.

        Raises:
            PmsError: If preferences cannot be loaded after initialization.
        """
        preferences = await Database.board_preferences.get(
            project_id=project_id, user_id=actor_id, session=session
        )
        if preferences:
            return preferences
        create = pydantic.BoardPreferenceCreateDTO(
            project_id=project_id,
            user_id=actor_id,
            display=DEFAULT_DISPLAY,
            collapsed_state_ids=[],
        )
        preferences = await Database.board_preferences.upsert(
            data=create,
            conflict_fields={"project_id", "user_id"},
            on_conflict="nothing",
            session=session,
            mode="json",
        )
        if preferences:
            return preferences
        preferences = await Database.board_preferences.get(
            project_id=project_id, user_id=actor_id, session=session
        )
        if preferences is None:
            raise PmsError(500, "INTERNAL_ERROR", "Board preferences could not be initialized.")
        return preferences

    @staticmethod
    def _preferences_api(preferences: pydantic.BoardPreferenceDTO) -> board_api.BoardPreferences:
        """Convert stored board preferences to their public representation."""

        return board_api.BoardPreferences(
            display=board_api.BoardDisplayProperties.model_validate(preferences.display),
            collapsed_state_ids=preferences.collapsed_state_ids,
            version=preferences.version,
        )

    @classmethod
    async def get_board(
        cls,
        workspace_slug: str,
        project_id: UUID,
        actor: pydantic.ActorDTO,
        queries: board_api.BoardQueries,
    ) -> board_api.BoardResponse:
        """Assemble a filtered board snapshot for a project actor.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project whose board is requested.
            actor: Request actor context.
            queries: Board filters and per-column page size.

        Returns:
            Project, permissions, columns, included entities, and user
            preferences in one board snapshot.

        Raises:
            PmsError: If filters are malformed or the actor cannot access the
                project.
        """
        priorities = parse_enum_csv(queries.priority, enum.Priority, "priority")
        assignee_ids = parse_uuid_csv(queries.assignee_id, "assignee_id")
        if queries.only_mine:
            assignee_ids = [actor.id]
        epic_id: UUID | str | None = queries.epic_id
        if epic_id and epic_id != "none":
            try:
                epic_id = UUID(epic_id)
            except ValueError as exc:
                raise PmsError(400, "MALFORMED_REQUEST", "Invalid epic_id filter.") from exc
        async with Services.database.session() as session:
            access = await AccessManager.require_project(session, actor, workspace_slug, project_id)
            states = await StatesManager._list(session, project_id)
            column_items = await Database.work_items.list_board_columns(
                session=session,
                project_id=project_id,
                search=queries.search,
                priorities=priorities,
                assignee_ids=assignee_ids,
                epic_id=epic_id,
                due_status=queries.due_status,
                per_column=queries.per_column,
            )
            all_items = [
                item
                for items, _ in column_items.values()
                for item in items
            ]
            mapped = await WorkItemsManager._assignee_map(
                session,
                [item.id for item in all_items],
            )
            columns = []
            for state in states:
                items, total = column_items.get(state.id, ([], 0))
                cards = [
                    WorkItemsManager._card(
                        item, access.project.identifier, mapped.get(item.id, [])
                    )
                    for item in items
                ]
                has_more = len(cards) < total
                columns.append(
                    board_api.BoardColumnSnapshot(
                        state=state,
                        work_items=cards,
                        page=common_api.CursorMeta(
                            next_cursor=encode_cursor(len(cards)) if has_more else None,
                            has_more=has_more,
                            total_count=total,
                        ),
                    )
                )
            epic_rows, epics_count = await Database.epics.list_with_progress(
                session, project_id, limit=100
            )
            epic_pickers = []
            for row in epic_rows:
                epic = pydantic.EpicDTO.model_validate(row)
                epic_pickers.append(
                    epic_api.EpicPickerItem(
                        id=epic.id,
                        identifier=f"{access.project.identifier}-E{epic.sequence_id}",
                        title=epic.title,
                        state_id=epic.state_id,
                        progress_percent=int(row.progress_percent),
                    )
                )
            preferences = await cls._preferences(session, project_id, actor.id)
            members = await member_summaries(session, project_id)
            project = await ProjectsManager._project_api(
                session,
                access.project,
                access.role,
                members,
                sum(state.work_items_count for state in states),
                epics_count,
            )
            result = board_api.BoardResponse(
                data=board_api.BoardSnapshot(
                    project=project,
                    permissions=access.permissions,
                    board_version=access.project.board_version,
                    columns=columns,
                    included=board_api.BoardIncluded(
                        members=members,
                        epics=epic_pickers,
                    ),
                    preferences=cls._preferences_api(preferences),
                )
            )
            emit_event("board_loaded", project_id=project_id, board_version=access.project.board_version)
            return result

    @classmethod
    async def get_preferences(
        cls,
        workspace_slug: str,
        project_id: UUID,
        actor: pydantic.ActorDTO,
    ) -> board_api.BoardPreferencesResponse:
        """Return the actor's board preferences, initializing defaults if needed.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project whose board preferences are requested.
            actor: Request actor context.

        Returns:
            The actor's current board preferences.

        Raises:
            PmsError: If the actor cannot access the project or preferences
                cannot be initialized.
        """
        async with Services.database.session() as session:
            await AccessManager.require_project(session, actor, workspace_slug, project_id)
            preferences = await cls._preferences(session, project_id, actor.id)
            return board_api.BoardPreferencesResponse(
                data=cls._preferences_api(preferences)
            )

    @classmethod
    async def update_preferences(
        cls,
        workspace_slug: str,
        project_id: UUID,
        actor: pydantic.ActorDTO,
        data: board_api.UpdateBoardPreferencesRequest,
    ) -> board_api.BoardPreferencesResponse:
        """Update display and collapsed-column preferences for an actor.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project whose preferences are updated.
            actor: Request actor context.
            data: Validated partial preference fields.

        Returns:
            The current or updated board preferences.

        Raises:
            PmsError: If access is denied, display keys are unknown, collapsed
                states are invalid, or the preference record disappears.
        """
        async with Services.database.session() as session:
            await AccessManager.require_project(session, actor, workspace_slug, project_id)
            current = await cls._preferences(session, project_id, actor.id)
            values = data.model_dump(exclude_unset=True)
            if not values:
                return board_api.BoardPreferencesResponse(
                    data=cls._preferences_api(current)
                )
            if data.display is not None:
                unknown = set(data.display) - set(DEFAULT_DISPLAY)
                if unknown:
                    raise PmsError(422, "VALIDATION_ERROR", "Unknown display preference.")
                values["display"] = {**current.display, **data.display}
            if data.collapsed_state_ids is not None:
                if len(data.collapsed_state_ids) != len(set(data.collapsed_state_ids)):
                    raise PmsError(422, "VALIDATION_ERROR", "collapsed_state_ids must be unique.")
                states = await Database.states.get_by_ids(
                    data.collapsed_state_ids, project_id=project_id, session=session
                )
                if {state.id for state in states} != set(data.collapsed_state_ids):
                    raise PmsError(422, "CROSS_PROJECT_REFERENCE", "Collapsed state does not belong to project.")
            values["version"] = current.version + 1
            preferences = await Database.board_preferences.update(
                id=current.id,
                data=pydantic.BoardPreferenceUpdateFieldsDTO(**values),
                project_id=project_id,
                user_id=actor.id,
                session=session,
            )
            if not preferences:
                raise PmsError(404, "PROJECT_NOT_FOUND", "Board preferences not found.")
            return board_api.BoardPreferencesResponse(
                data=cls._preferences_api(preferences)
            )
