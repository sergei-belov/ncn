from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query

from api.dependencies.http import (
    get_project_actor,
    reject_unknown_query_params,
)
from api.managers.managers import Managers
from models import pydantic


router = APIRouter(
    prefix="/api/v1/workspaces/{workspace_slug}/projects/{project_id}",
    tags=["Board"],
)
NO_QUERY_PARAMS = Depends(reject_unknown_query_params())


@router.get("/board", response_model=pydantic.BoardResponse)
async def get_board(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    queries: Annotated[pydantic.BoardQueries, Query()],
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Return a filtered snapshot of a project's board."""

    return await Managers.board.get_board(workspace_slug, project_id, actor, queries)


@router.get(
    "/board-preferences",
    response_model=pydantic.BoardPreferencesResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def get_board_preferences(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Return the authenticated actor's board preferences."""

    return await Managers.board.get_preferences(workspace_slug, project_id, actor)


@router.patch(
    "/board-preferences",
    response_model=pydantic.BoardPreferencesResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def update_board_preferences(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    body: pydantic.UpdateBoardPreferencesRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Update the authenticated actor's board preferences."""

    return await Managers.board.update_preferences(
        workspace_slug, project_id, actor, body
    )
