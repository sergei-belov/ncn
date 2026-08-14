from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, status

from api.dependencies.http import (
    get_project_actor,
    get_workspace_actor,
    reject_unknown_query_params,
)
from api.managers.managers import Managers
from models import pydantic


router = APIRouter(prefix="/api/v1/workspaces/{workspace_slug}/projects", tags=["Projects"])
NO_QUERY_PARAMS = Depends(reject_unknown_query_params())


@router.get("", response_model=pydantic.ProjectListResponse)
async def list_projects(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    queries: Annotated[pydantic.ProjectListQueries, Query()],
    actor: Annotated[pydantic.ActorDTO, Depends(get_workspace_actor)],
):
    """List projects visible to the workspace actor."""

    return await Managers.projects.list_projects(workspace_slug, actor, queries)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=pydantic.ProjectResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def create_project(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    body: pydantic.CreateProjectRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_workspace_actor)],
):
    """Create and initialize a workspace project."""

    return await Managers.projects.create_project(workspace_slug, actor, body)


@router.get(
    "/{project_id}",
    response_model=pydantic.ProjectResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def get_project(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Retrieve an actor-visible project."""

    return await Managers.projects.get_project(workspace_slug, project_id, actor)


@router.patch(
    "/{project_id}",
    response_model=pydantic.ProjectResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def update_project(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    body: pydantic.UpdateProjectRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Update mutable fields of a project."""

    return await Managers.projects.update_project(workspace_slug, project_id, actor, body)


@router.post(
    "/{project_id}/archive",
    response_model=pydantic.ProjectResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def archive_project(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    body: pydantic.ArchiveProjectRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Archive a project after name confirmation."""

    return await Managers.projects.archive_project(workspace_slug, project_id, actor, body)


@router.post(
    "/{project_id}/restore",
    response_model=pydantic.ProjectResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def restore_project(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    _body: pydantic.RestoreProjectRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Restore an archived project."""

    return await Managers.projects.restore_project(workspace_slug, project_id, actor)
