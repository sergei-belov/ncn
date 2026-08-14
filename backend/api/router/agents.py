from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, status

from api.dependencies.http import (
    get_project_actor,
    reject_unknown_query_params,
)
from api.managers.managers import Managers
from models import pydantic


router = APIRouter(
    prefix="/api/v1/workspaces/{workspace_slug}/projects/{project_id}/agents",
    tags=["Agents"],
)
NO_QUERY_PARAMS = Depends(reject_unknown_query_params())


@router.get(
    "",
    response_model=pydantic.AgentListResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def list_agents(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """List agents configured for a project."""

    return await Managers.agents.list_agents(workspace_slug, project_id, actor)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=pydantic.AgentResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def create_agent(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    body: pydantic.CreateAgentRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Create a worker agent in a project."""

    return await Managers.agents.create_agent(
        workspace_slug,
        project_id,
        actor,
        body,
    )


@router.get(
    "/{agent_id}",
    response_model=pydantic.AgentResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def get_agent(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    agent_id: UUID,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Retrieve one project agent."""

    return await Managers.agents.get_agent(
        workspace_slug,
        project_id,
        agent_id,
        actor,
    )


@router.patch(
    "/{agent_id}",
    response_model=pydantic.AgentResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def update_agent(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    agent_id: UUID,
    body: pydantic.UpdateAgentRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Update an agent under optimistic concurrency."""

    return await Managers.agents.update_agent(
        workspace_slug,
        project_id,
        agent_id,
        actor,
        body,
        body.expected_version,
    )


@router.post(
    "/{agent_id}/enable",
    response_model=pydantic.AgentResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def enable_agent(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    agent_id: UUID,
    body: pydantic.AgentCommandRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Enable a project agent under optimistic concurrency."""

    return await Managers.agents.set_agent_enabled(
        workspace_slug,
        project_id,
        agent_id,
        actor,
        True,
        body.expected_version,
    )


@router.post(
    "/{agent_id}/disable",
    response_model=pydantic.AgentResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def disable_agent(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    agent_id: UUID,
    body: pydantic.AgentCommandRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Disable a project agent under optimistic concurrency."""

    return await Managers.agents.set_agent_enabled(
        workspace_slug,
        project_id,
        agent_id,
        actor,
        False,
        body.expected_version,
    )


@router.post(
    "/{agent_id}/archive",
    response_model=pydantic.AgentResponse,
    dependencies=[NO_QUERY_PARAMS],
)
async def archive_agent(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: UUID,
    agent_id: UUID,
    body: pydantic.AgentCommandRequest,
    actor: Annotated[pydantic.ActorDTO, Depends(get_project_actor)],
):
    """Archive a project agent under optimistic concurrency."""

    return await Managers.agents.archive_agent(
        workspace_slug,
        project_id,
        agent_id,
        actor,
        body.expected_version,
    )
