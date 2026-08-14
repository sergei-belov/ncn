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
    prefix="/api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items",
    tags=["Work items"],
)
NO_QUERY_PARAMS = Depends(reject_unknown_query_params())


@router.get("", response_model=pydantic.WorkItemPage)
async def list_work_items(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    queries: Annotated[pydantic.WorkItemListQueries, Query()],
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """List filtered work items for a project."""

    return await Managers.work_items.list_work_items(workspace_slug, project_id, actor, queries)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=pydantic.WorkItemResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def create_work_item(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    body: pydantic.CreateWorkItemRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Create and position a work item."""

    return await Managers.work_items.create_work_item(
        workspace_slug, project_id, actor, body
    )


@router.get(
    "/{work_item_id}",
    response_model=pydantic.WorkItemDetailResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def get_work_item(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    work_item_id: UUID,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Retrieve a work item with related project entities."""

    return await Managers.work_items.get_work_item(
        workspace_slug, project_id, work_item_id, actor
    )


@router.patch(
    "/{work_item_id}",
    response_model=pydantic.WorkItemResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def update_work_item(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    work_item_id: UUID,
    body: pydantic.UpdateWorkItemRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Update mutable work-item fields."""

    return await Managers.work_items.update_work_item(
        workspace_slug, project_id, work_item_id, actor, body
    )


@router.post(
    "/{work_item_id}/move",
    response_model=pydantic.MoveWorkItemResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def move_work_item(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    work_item_id: UUID,
    body: pydantic.MoveWorkItemRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Move a work item under optimistic concurrency."""

    return await Managers.work_items.move_work_item(
        workspace_slug, project_id, work_item_id, actor, body
    )


@router.delete(
    "/{work_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[NO_QUERY_PARAMS],
)
async def delete_work_item(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    work_item_id: UUID,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Delete a work item from a project."""

    await Managers.work_items.delete_work_item(
        workspace_slug, project_id, work_item_id, actor
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
