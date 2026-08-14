from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, Response, status

from api.dependencies.http import (
    get_project_actor,
    reject_unknown_query_params,
)
from api.managers.managers import Managers
from models import pydantic


router = APIRouter(
    prefix="/api/v1/workspaces/{workspace_slug}/projects/{project_id}/states",
    tags=["States"],
)
NO_QUERY_PARAMS = Depends(reject_unknown_query_params())
REPLACEMENT_QUERY_PARAM = Depends(reject_unknown_query_params("replacement_state_id"))


@router.get(
    "",
    response_model=pydantic.StateListResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def list_states(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """List a project's workflow states in board order."""

    return await Managers.states.list_states(workspace_slug, project_id, actor)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=pydantic.StateResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def create_state(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    body: pydantic.CreateStateRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Create and position a workflow state."""

    return await Managers.states.create_state(workspace_slug, project_id, actor, body)


@router.post(
    "/reorder",
    response_model=pydantic.ReorderStatesResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def reorder_states(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    body: pydantic.ReorderStatesRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Replace the full workflow-state ordering."""

    return await Managers.states.reorder_states(workspace_slug, project_id, actor, body)


@router.patch(
    "/{state_id}",
    response_model=pydantic.StateResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def update_state(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    state_id: UUID,
    body: pydantic.UpdateStateRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Update mutable workflow-state fields."""

    return await Managers.states.update_state(
        workspace_slug, project_id, state_id, actor, body
    )


@router.delete(
    "/{state_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[REPLACEMENT_QUERY_PARAM],
)
async def delete_state(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    state_id: UUID,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
    replacement_state_id: Annotated[UUID | None, Query()] = None,
):
    """Delete a state and optionally move its entities to a replacement."""

    await Managers.states.delete_state(
        workspace_slug,
        project_id,
        state_id,
        replacement_state_id,
        actor,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
