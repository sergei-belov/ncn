from uuid import UUID

from api.db.db import Database
from api.managers.common import (
    AccessManager,
    PmsError,
    emit_event,
)
from api.services import Services
from models import pydantic
from models.pydantic.api import state_api


class StatesManager:
    """Manage project workflow states and their board ordering."""

    @staticmethod
    def _state_api(row) -> state_api.State:
        """Convert a state aggregate row to its API representation."""

        state = pydantic.ProjectStateDTO.model_validate(row)
        return state_api.State(**state.model_dump(), work_items_count=int(row.work_items_count))

    @classmethod
    async def _list(cls, session, project_id: UUID) -> list[state_api.State]:
        """Load project states with work-item counts in board order."""

        rows = await Database.states.list_with_counts(session, project_id)
        return [cls._state_api(row) for row in rows]

    @classmethod
    async def list_states(
        cls, workspace_slug: str, project_id: UUID, actor: pydantic.ActorDTO
    ) -> state_api.StateListResponse:
        """List workflow states visible to a project actor.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project whose states are requested.
            actor: Request actor context.

        Returns:
            Ordered workflow states with work-item counts.

        Raises:
            PmsError: If the actor cannot access the project.
        """
        async with Services.database.session() as session:
            await AccessManager.require_project(session, actor, workspace_slug, project_id)
            return state_api.StateListResponse(data=await cls._list(session, project_id))

    @classmethod
    async def create_state(
        cls,
        workspace_slug: str,
        project_id: UUID,
        actor: pydantic.ActorDTO,
        data: state_api.CreateStateRequest,
    ) -> state_api.StateResponse:
        """Create an idempotent workflow state and place it on the board.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project receiving the state.
            actor: Request actor context.
            data: Validated state creation fields.

        Returns:
            The created or pre-existing state and current board metadata.

        Raises:
            PmsError: If access is denied, the supplied ID belongs elsewhere,
                the name is duplicated, or the insertion anchor is invalid.
        """
        async with Services.database.session() as session:
            await AccessManager.require_project(
                session, actor, workspace_slug, project_id, "can_manage_states"
            )
            existing_state = await Database.states.get(id=data.id, session=session)
            if existing_state:
                if existing_state.project_id != project_id:
                    raise PmsError(
                        422,
                        "CROSS_PROJECT_REFERENCE",
                        "State id belongs to another project.",
                    )
                row = next(
                    row
                    for row in await Database.states.list_with_counts(session, project_id)
                    if row[0].id == existing_state.id
                )
                return state_api.StateResponse(data=cls._state_api(row))
            existing = await Database.states.get_list(
                project_id=project_id, sort_by="position", session=session
            )
            if any(state.name.casefold() == data.name.casefold() for state in existing):
                raise PmsError(422, "VALIDATION_ERROR", "State name must be unique.")
            ordered_ids = [state.id for state in existing]
            if data.after_state_id:
                if data.after_state_id not in ordered_ids:
                    raise PmsError(422, "CROSS_PROJECT_REFERENCE", "after_state_id is not in this project.")
                insert_at = ordered_ids.index(data.after_state_id) + 1
            else:
                insert_at = len(ordered_ids)
            state_create = pydantic.ProjectStateCreateDTO(
                id=data.id,
                project_id=project_id,
                name=data.name,
                color=data.color.upper(),
                group=data.group,
                position=len(existing),
                is_default=data.is_default,
            )
            if data.is_default:
                await Database.states.clear_default(session, project_id, state_create.id)
            state = await Database.states.create(
                state_create,
                session=session,
                mode="json",
            )
            ordered_ids.insert(insert_at, state.id)
            await Database.states.set_positions(session, project_id, ordered_ids)
            if data.is_default:
                await Database.projects.update(
                    project_id,
                    pydantic.ProjectUpdateFieldsDTO(default_state_id=state.id),
                    session=session,
                )
            board_version = await Database.projects.increment_board_version(session, project_id)
            rows = await Database.states.list_with_counts(session, project_id)
            created_row = next(row for row in rows if row[0].id == state.id)
            result = state_api.StateResponse(
                data=cls._state_api(created_row), meta={"board_version": board_version}
            )
            emit_event("state_created", project_id=project_id, state_id=state.id)
            return result

    @classmethod
    async def update_state(
        cls,
        workspace_slug: str,
        project_id: UUID,
        state_id: UUID,
        actor: pydantic.ActorDTO,
        data: state_api.UpdateStateRequest,
    ) -> state_api.StateResponse:
        """Update workflow-state fields and related project defaults.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project that owns the state.
            state_id: State to update.
            actor: Request actor context.
            data: Validated partial update fields.

        Returns:
            The updated state and current board metadata.

        Raises:
            PmsError: If access is denied, the state is missing, the name is
                duplicated, or the current default is unset without replacement.
        """
        async with Services.database.session() as session:
            await AccessManager.require_project(
                session, actor, workspace_slug, project_id, "can_manage_states"
            )
            current = await Database.states.get(
                id=state_id,
                project_id=project_id,
                session=session,
            )
            if not current:
                raise PmsError(404, "STATE_NOT_FOUND", "State not found.")
            values = data.model_dump(exclude_unset=True)
            if not values:
                row = next(
                    row
                    for row in await Database.states.list_with_counts(session, project_id)
                    if row[0].id == state_id
                )
                return state_api.StateResponse(data=cls._state_api(row))
            if "name" in values:
                states = await Database.states.get_list(
                    project_id=project_id,
                    session=session,
                )
                if any(
                    state.id != state_id
                    and state.name.casefold() == values["name"].casefold()
                    for state in states
                ):
                    raise PmsError(422, "VALIDATION_ERROR", "State name must be unique.")
            if "color" in values and values["color"]:
                values["color"] = values["color"].upper()
            if values.get("is_default") is False and current.is_default:
                raise PmsError(422, "VALIDATION_ERROR", "Select another default state first.")
            if values.get("is_default"):
                await Database.states.clear_default(session, project_id, state_id)
            values["version"] = current.version + 1
            state = await Database.states.update(
                id=state_id,
                data=pydantic.ProjectStateUpdateFieldsDTO(**values),
                project_id=project_id,
                session=session,
            )
            if not state:
                raise PmsError(404, "STATE_NOT_FOUND", "State not found.")
            if values.get("is_default"):
                await Database.projects.update(
                    project_id,
                    pydantic.ProjectUpdateFieldsDTO(default_state_id=state_id),
                    session=session,
                )
            board_version = await Database.projects.increment_board_version(session, project_id)
            row = next(
                row
                for row in await Database.states.list_with_counts(session, project_id)
                if row[0].id == state_id
            )
            return state_api.StateResponse(
                data=cls._state_api(row), meta={"board_version": board_version}
            )

    @classmethod
    async def reorder_states(
        cls,
        workspace_slug: str,
        project_id: UUID,
        actor: pydantic.ActorDTO,
        data: state_api.ReorderStatesRequest,
    ) -> state_api.ReorderStatesResponse:
        """Replace the complete state ordering under optimistic concurrency.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project whose states are reordered.
            actor: Request actor context.
            data: Complete ordering and expected board version.

        Returns:
            Reordered states and the resulting board version.

        Raises:
            PmsError: If access is denied, the ordering is incomplete, or the
                expected board version is stale.
        """
        async with Services.database.session() as session:
            access = await AccessManager.require_project(
                session, actor, workspace_slug, project_id, "can_manage_states"
            )
            project = access.project
            current = await Database.states.get_list(project_id=project_id, session=session)
            if len(data.ordered_state_ids) != len(set(data.ordered_state_ids)) or set(data.ordered_state_ids) != {
                state.id for state in current
            }:
                raise PmsError(422, "VALIDATION_ERROR", "ordered_state_ids must contain every state exactly once.")
            current_ids = [
                state.id
                for state in sorted(current, key=lambda value: (value.position, value.id))
            ]
            if current_ids == data.ordered_state_ids:
                return state_api.ReorderStatesResponse(
                    data=state_api.ReorderStatesData(
                        states=await cls._list(session, project_id),
                        board_version=project.board_version,
                    )
                )
            if project.board_version != data.expected_board_version:
                raise PmsError(
                    409,
                    "BOARD_VERSION_CONFLICT",
                    "Board version is stale.",
                    details={"board_version": project.board_version},
                )
            await Database.states.set_positions(session, project_id, data.ordered_state_ids)
            board_version = await Database.projects.increment_board_version(session, project_id)
            result = state_api.ReorderStatesResponse(
                data=state_api.ReorderStatesData(
                    states=await cls._list(session, project_id), board_version=board_version
                )
            )
            emit_event("state_reordered", project_id=project_id, board_version=board_version)
            return result

    @classmethod
    async def delete_state(
        cls,
        workspace_slug: str,
        project_id: UUID,
        state_id: UUID,
        replacement_state_id: UUID | None,
        actor: pydantic.ActorDTO,
    ) -> None:
        """Delete a state after optionally moving its owned entities.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project that owns the state.
            state_id: State to delete.
            replacement_state_id: State that receives existing work items and
                epics, when required.
            actor: Request actor context.

        Raises:
            PmsError: If access is denied, deletion would violate state
                invariants, or the replacement state is invalid.
        """
        async with Services.database.session() as session:
            await AccessManager.require_project(
                session, actor, workspace_slug, project_id, "can_manage_states"
            )
            state = await Database.states.get(
                id=state_id,
                project_id=project_id,
                session=session,
            )
            if not state:
                raise PmsError(404, "STATE_NOT_FOUND", "State not found.")
            states = await Database.states.get_list(project_id=project_id, session=session)
            if len(states) == 1:
                raise PmsError(409, "CANNOT_DELETE_LAST_STATE", "The last state cannot be deleted.")
            if state.is_default:
                raise PmsError(409, "CANNOT_DELETE_DEFAULT_STATE", "The default state cannot be deleted.")
            work_items = await Database.work_items.get_list(
                project_id=project_id, state_id=state_id, sort_by="rank", session=session
            )
            epics = await Database.epics.get_list(
                project_id=project_id, state_id=state_id, sort_by="rank", session=session
            )
            if (work_items or epics) and replacement_state_id is None:
                raise PmsError(409, "STATE_NOT_EMPTY", "A replacement state is required.")
            if replacement_state_id == state_id:
                raise PmsError(422, "INVALID_REPLACEMENT_STATE", "Replacement state must be different.")
            if replacement_state_id:
                replacement = await Database.states.get(
                    id=replacement_state_id, project_id=project_id, session=session
                )
                if not replacement:
                    raise PmsError(422, "INVALID_REPLACEMENT_STATE", "Replacement state is invalid.")
                for item in work_items:
                    rank, _, _ = await Database.work_items.allocate_rank(
                        session, project_id, replacement_state_id, None, None, item.id
                    )
                    await Database.work_items.update(
                        id=item.id,
                        data=pydantic.WorkItemUpdateFieldsDTO(
                            state_id=replacement_state_id,
                            rank=rank,
                            version=item.version + 1,
                        ),
                        project_id=project_id,
                        session=session,
                    )
                for epic in epics:
                    await Database.epics.update(
                        id=epic.id,
                        data=pydantic.EpicUpdateFieldsDTO(
                            state_id=replacement_state_id,
                            version=epic.version + 1,
                        ),
                        project_id=project_id,
                        session=session,
                    )
            await Database.states.delete(state_id, project_id=project_id, session=session)
            remaining_ids = [
                item.id
                for item in sorted(states, key=lambda value: value.position)
                if item.id != state_id
            ]
            await Database.states.set_positions(session, project_id, remaining_ids)
            await Database.projects.increment_board_version(session, project_id)
