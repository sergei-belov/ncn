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
    prefix="/api/v1/workspaces/{workspace_slug}/projects/{project_id}/epics",
    tags=["Epics"],
)
NO_QUERY_PARAMS = Depends(reject_unknown_query_params())
EPIC_ITEMS_QUERY_PARAMS = Depends(
    reject_unknown_query_params("search", "cursor", "limit")
)


@router.get("", response_model=pydantic.EpicPage)
async def list_epics(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    queries: Annotated[pydantic.EpicListQueries, Query()],
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """List filtered epics for a project."""

    return await Managers.epics.list_epics(workspace_slug, project_id, actor, queries)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=pydantic.EpicResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def create_epic(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    body: pydantic.CreateEpicRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Create an epic in a project."""

    return await Managers.epics.create_epic(
        workspace_slug, project_id, actor, body
    )


@router.get(
    "/{epic_id}",
    response_model=pydantic.EpicDetailResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def get_epic(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    epic_id: UUID,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Retrieve an epic with related project entities."""

    return await Managers.epics.get_epic(workspace_slug, project_id, epic_id, actor)


@router.patch(
    "/{epic_id}",
    response_model=pydantic.EpicResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def update_epic(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    epic_id: UUID,
    body: pydantic.UpdateEpicRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Update mutable epic fields."""

    return await Managers.epics.update_epic(
        workspace_slug, project_id, epic_id, actor, body
    )


@router.delete(
    "/{epic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[NO_QUERY_PARAMS],
)
async def delete_epic(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    epic_id: UUID,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Delete an epic and detach its work items."""

    await Managers.epics.delete_epic(workspace_slug, project_id, epic_id, actor)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{epic_id}/work-items",
    response_model=pydantic.WorkItemPage,
    dependencies=[EPIC_ITEMS_QUERY_PARAMS],
)
async def list_epic_work_items(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    epic_id: UUID,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
    search: Annotated[str | None, Query()] = None,
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 30,
):
    """List work items linked to an epic."""

    return await Managers.epics.list_epic_work_items(
        workspace_slug, project_id, epic_id, actor, search, cursor, limit
    )


@router.post(
    "/{epic_id}/work-items",
    response_model=pydantic.EpicWorkItemsMutationResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def add_epic_work_items(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    epic_id: UUID,
    body: pydantic.AddEpicWorkItemsRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Attach one or more work items to an epic."""

    return await Managers.epics.add_work_items(
        workspace_slug, project_id, epic_id, actor, body
    )


@router.delete(
    "/{epic_id}/work-items/{work_item_id}",
    response_model=pydantic.EpicWorkItemsMutationResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def remove_epic_work_item(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    epic_id: UUID,
    work_item_id: UUID,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Detach one work item from an epic."""

    return await Managers.epics.remove_work_item(
        workspace_slug, project_id, epic_id, work_item_id, actor
    )
