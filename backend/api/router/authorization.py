from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, Response, status

from api.dependencies.http import get_user
from api.managers import Managers
from models import pydantic


router = APIRouter(prefix="/api/v1", tags=["Authorization"])


@router.post("/authorization/check", response_model=pydantic.AuthorizationCheckResponse)
async def check_authorization(
    body: pydantic.AuthorizationCheckRequest,
    actor: Annotated[pydantic.UserDTO, Depends(get_user)],
) -> pydantic.AuthorizationCheckResponse:
    """Return the current named-action decision for the authenticated user."""

    return await Managers.authorization.check_authorization(actor, body)


@router.get(
    "/workspaces/{workspace_id}/members",
    response_model=pydantic.WorkspaceMembershipList,
)
async def list_workspace_members(
    workspace_id: Annotated[str, Path(min_length=1, max_length=100)],
    queries: Annotated[pydantic.MembershipListQueries, Query()],
    actor: Annotated[pydantic.UserDTO, Depends(get_user)],
) -> pydantic.WorkspaceMembershipList:
    """List workspace memberships visible to an authorized administrator."""

    return await Managers.authorization.list_workspace_members(workspace_id, actor, queries)


@router.post(
    "/workspaces/{workspace_id}/members",
    response_model=pydantic.WorkspaceMembership,
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace_member(
    workspace_id: Annotated[str, Path(min_length=1, max_length=100)],
    body: pydantic.CreateWorkspaceMembershipRequest,
    actor: Annotated[pydantic.UserDTO, Depends(get_user)],
) -> pydantic.WorkspaceMembership:
    """Grant workspace access under scoped role guards."""

    return await Managers.authorization.create_workspace_member(workspace_id, actor, body)


@router.patch(
    "/workspaces/{workspace_id}/members/{user_id}",
    response_model=pydantic.WorkspaceMembership,
)
async def update_workspace_member(
    workspace_id: Annotated[str, Path(min_length=1, max_length=100)],
    user_id: UUID,
    body: pydantic.UpdateWorkspaceMembershipRequest,
    actor: Annotated[pydantic.UserDTO, Depends(get_user)],
) -> pydantic.WorkspaceMembership:
    """Change a workspace role with optimistic concurrency."""

    return await Managers.authorization.update_workspace_member(
        workspace_id,
        user_id,
        actor,
        body,
    )


@router.post(
    "/workspaces/{workspace_id}/members/{user_id}/revoke",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revoke_workspace_member(
    workspace_id: Annotated[str, Path(min_length=1, max_length=100)],
    user_id: UUID,
    body: pydantic.RevokeMembershipRequest,
    actor: Annotated[pydantic.UserDTO, Depends(get_user)],
) -> None:
    """Revoke workspace access with version and last-owner protection."""

    await Managers.authorization.revoke_workspace_member(workspace_id, user_id, actor, body)


@router.get(
    "/projects/{project_id}/members",
    response_model=pydantic.ProjectMembershipList,
)
async def list_project_members(
    project_id: UUID,
    queries: Annotated[pydantic.MembershipListQueries, Query()],
    actor: Annotated[pydantic.UserDTO, Depends(get_user)],
) -> pydantic.ProjectMembershipList:
    """List project memberships and service restrictions for an admin."""

    return await Managers.authorization.list_project_members(project_id, actor, queries)


@router.post(
    "/projects/{project_id}/members",
    response_model=pydantic.ProjectMembership,
    status_code=status.HTTP_201_CREATED,
)
async def create_project_member(
    project_id: UUID,
    body: pydantic.CreateProjectMembershipRequest,
    actor: Annotated[pydantic.UserDTO, Depends(get_user)],
) -> pydantic.ProjectMembership:
    """Grant project access under admin and role-ceiling guards."""

    return await Managers.authorization.create_project_member(project_id, actor, body)


@router.patch(
    "/projects/{project_id}/members/{user_id}",
    response_model=pydantic.ProjectMembership,
)
async def update_project_member(
    project_id: UUID,
    user_id: UUID,
    body: pydantic.UpdateProjectMembershipRequest,
    actor: Annotated[pydantic.UserDTO, Depends(get_user)],
) -> pydantic.ProjectMembership:
    """Change a project role with version and last-admin protection."""

    return await Managers.authorization.update_project_member(project_id, user_id, actor, body)


@router.post(
    "/projects/{project_id}/members/{user_id}/revoke",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revoke_project_member(
    project_id: UUID,
    user_id: UUID,
    body: pydantic.RevokeMembershipRequest,
    actor: Annotated[pydantic.UserDTO, Depends(get_user)],
) -> None:
    """Revoke project access with version and last-admin protection."""

    await Managers.authorization.revoke_project_member(project_id, user_id, actor, body)


@router.put(
    "/projects/{project_id}/members/{user_id}/services/{service_id}",
    response_model=pydantic.ServiceRestrictionResult,
)
async def put_service_restriction(
    response: Response,
    project_id: UUID,
    user_id: UUID,
    service_id: Annotated[
        str,
        Path(min_length=1, max_length=100, pattern=r"^[a-z0-9][a-z0-9._-]{0,99}$"),
    ],
    body: pydantic.PutServiceRestrictionRequest,
    actor: Annotated[pydantic.UserDTO, Depends(get_user)],
) -> pydantic.ServiceRestrictionResult:
    """Create or replace a narrowing project-service restriction."""

    result, created = await Managers.authorization.put_service_restriction(
        project_id,
        user_id,
        service_id,
        actor,
        body,
    )
    if created:
        response.status_code = status.HTTP_201_CREATED
    return result


@router.delete(
    "/projects/{project_id}/members/{user_id}/services/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_service_restriction(
    project_id: UUID,
    user_id: UUID,
    service_id: Annotated[
        str,
        Path(min_length=1, max_length=100, pattern=r"^[a-z0-9][a-z0-9._-]{0,99}$"),
    ],
    body: pydantic.DeleteServiceRestrictionRequest,
    actor: Annotated[pydantic.UserDTO, Depends(get_user)],
) -> None:
    """Remove a restriction and restore inherited project access."""

    await Managers.authorization.delete_service_restriction(
        project_id,
        user_id,
        service_id,
        actor,
        body,
    )


@router.put(
    "/projects/{project_id}/creator-access",
    response_model=pydantic.ProjectMembership,
)
async def bootstrap_creator_access(
    response: Response,
    project_id: UUID,
    body: pydantic.BootstrapCreatorAccessRequest,
    actor: Annotated[pydantic.UserDTO, Depends(get_user)],
) -> pydantic.ProjectMembership:
    """Converge creator-admin access in the current shared deployment."""

    result, created = await Managers.authorization.bootstrap_creator_access(
        project_id,
        actor,
        body,
    )
    if created:
        response.status_code = status.HTTP_201_CREATED
    return result
