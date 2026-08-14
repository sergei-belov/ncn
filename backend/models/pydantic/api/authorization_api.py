from datetime import datetime
from uuid import UUID

from pydantic import Field

from models import enum
from models.pydantic.api.common_api import APIModel


class AuthorizationResource(APIModel):
    """Consumer-owned resource reference validated against an action scope."""

    type: str = Field(min_length=1, max_length=50)
    id: str = Field(min_length=1, max_length=100)


class AuthorizationCheckRequest(APIModel):
    """Internal request for one current named authorization decision."""

    user_id: UUID
    action: str = Field(min_length=1, max_length=100)
    workspace_id: str | None = Field(default=None, min_length=1, max_length=100)
    project_id: UUID | None = None
    service_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9][a-z0-9._-]{0,99}$",
    )
    resource: AuthorizationResource | None = None


class AuthorizationCheckResponse(APIModel):
    """Current allow or deny result for a registered action."""

    allowed: bool
    reason: enum.AuthorizationDecisionReason
    effective_role: enum.WorkspaceRole | enum.ProjectRole | None
    effective_scope: enum.AuthorizationScope | None
    policy_version: str


class AccessUserSummary(APIModel):
    """Safe user fields shown to an authorized membership administrator."""

    id: UUID
    email: str
    name: str
    is_active: bool


class WorkspaceMembership(APIModel):
    """Canonical workspace membership returned by access APIs."""

    id: UUID
    workspace_id: str
    user_id: UUID
    role: enum.WorkspaceRole
    version: int = Field(ge=1)
    created_at: datetime
    updated_at: datetime


class WorkspaceMembershipItem(WorkspaceMembership):
    """Workspace membership enriched with its user's display fields."""

    user: AccessUserSummary


class ProjectMembership(APIModel):
    """Canonical project membership returned by access APIs."""

    id: UUID
    workspace_id: str
    project_id: UUID
    user_id: UUID
    role: enum.ProjectRole
    source: enum.ProjectMembershipSource
    version: int = Field(ge=1)
    created_at: datetime
    updated_at: datetime


class ServiceRestriction(APIModel):
    """Canonical explicit project-service role restriction."""

    id: UUID
    project_user_id: UUID
    service_id: str
    role: enum.ProjectRole
    version: int = Field(ge=1)
    created_at: datetime
    updated_at: datetime


class ServiceRestrictionResult(ServiceRestriction):
    """Service restriction together with its resulting effective role."""

    effective_role: enum.ProjectRole


class ProjectMembershipItem(ProjectMembership):
    """Project membership enriched with user and service access details."""

    user: AccessUserSummary
    service_restrictions: list[ServiceRestriction]


class MembershipListQueries(APIModel):
    """Bounded cursor and search options shared by membership lists."""

    cursor: str | None = Field(default=None, max_length=512)
    limit: int = Field(default=50, ge=1, le=100)
    search: str | None = Field(default=None, max_length=100)


class WorkspaceMembershipList(APIModel):
    """Cursor page of canonical workspace memberships."""

    items: list[WorkspaceMembershipItem]
    next_cursor: str | None = None


class ProjectMembershipList(APIModel):
    """Cursor page of canonical project memberships."""

    items: list[ProjectMembershipItem]
    next_cursor: str | None = None


class CreateWorkspaceMembershipRequest(APIModel):
    """Payload for granting workspace access to an active user."""

    user_id: UUID
    role: enum.WorkspaceRole


class UpdateWorkspaceMembershipRequest(APIModel):
    """Optimistic payload for changing a workspace role."""

    role: enum.WorkspaceRole
    expected_version: int = Field(ge=1)


class RevokeMembershipRequest(APIModel):
    """Optimistic payload for revoking a workspace or project membership."""

    expected_version: int = Field(ge=1)


class CreateProjectMembershipRequest(APIModel):
    """Payload for granting project access to an active user."""

    user_id: UUID
    role: enum.ProjectRole


class UpdateProjectMembershipRequest(APIModel):
    """Optimistic payload for changing a project role."""

    role: enum.ProjectRole
    expected_version: int = Field(ge=1)


class PutServiceRestrictionRequest(APIModel):
    """Payload for creating or replacing a service restriction."""

    role: enum.ProjectRole
    expected_version: int | None = Field(default=None, ge=1)


class DeleteServiceRestrictionRequest(APIModel):
    """Optimistic payload for removing a service restriction."""

    expected_version: int = Field(ge=1)


class BootstrapCreatorAccessRequest(APIModel):
    """PMS-owned scope and creator identity used for project bootstrap."""

    workspace_id: str = Field(min_length=1, max_length=100)
    creator_user_id: UUID
