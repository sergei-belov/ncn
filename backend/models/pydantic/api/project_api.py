from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from models import enum
from models.pydantic.api.common_api import (
    APIModel,
    CursorMeta,
    IconValue,
    MemberSummary,
    ProjectPermissions,
    WorkspaceProjectPermissions,
)


class ProjectListItem(APIModel):
    """Project summary enriched for workspace list views."""

    id: UUID
    workspace_slug: str
    name: str
    identifier: str
    description: str | None
    icon: IconValue
    color: str
    access: enum.ProjectAccess
    role: enum.ProjectRole
    permissions: ProjectPermissions
    member_preview: list[MemberSummary]
    total_members: int
    active_work_items_count: int
    epics_count: int
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime
    version: int


class Project(ProjectListItem):
    """Complete public project representation."""

    member_ids: list[UUID]
    default_state_id: UUID


class ProjectListMeta(CursorMeta):
    """Project-list cursor metadata with workspace capabilities."""

    permissions: WorkspaceProjectPermissions


class ProjectListResponse(APIModel):
    """Response envelope containing a page of project summaries."""

    data: list[ProjectListItem]
    meta: ProjectListMeta


class ProjectResponse(APIModel):
    """Response envelope containing one complete project."""

    data: Project
    meta: dict | None = None


class CreateProjectRequest(APIModel):
    """Validated idempotent project creation payload."""

    id: UUID = Field(description="Client-generated project and idempotency identifier")
    name: str = Field(min_length=1, max_length=255)
    identifier: str = Field(pattern=r"^[A-Z0-9]{2,10}$")
    description: str | None = Field(default=None, max_length=2000)
    icon: IconValue | None = None
    color: str = Field(default="#5E6AD2", pattern=r"^#[0-9A-Fa-f]{6}$")
    access: enum.ProjectAccess = enum.ProjectAccess.PRIVATE

    @field_validator("name")
    @classmethod
    def trim_name(cls, value: str) -> str:
        """Strip a project name and reject blank content."""

        value = value.strip()
        if not value:
            raise ValueError("name must not be blank")
        return value

    @field_validator("identifier", mode="before")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        """Strip and uppercase a project identifier."""

        return value.strip().upper()

    @model_validator(mode="after")
    def reject_non_nullable_nulls(self):
        """Reject explicit nulls for non-nullable creation fields."""

        forbidden = {"name", "identifier", "icon", "color", "access"}
        if any(field in self.model_fields_set and getattr(self, field) is None for field in forbidden):
            raise ValueError("Project fields other than description cannot be null")
        return self


class UpdateProjectRequest(APIModel):
    """Validated partial project update payload."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    identifier: str | None = Field(default=None, pattern=r"^[A-Z0-9]{2,10}$")
    description: str | None = Field(default=None, max_length=2000)
    icon: IconValue | None = None
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    access: enum.ProjectAccess | None = None

    @field_validator("name")
    @classmethod
    def trim_name(cls, value: str | None) -> str | None:
        """Strip a supplied project name and reject blank content."""

        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("name must not be blank")
        return value

    @field_validator("identifier", mode="before")
    @classmethod
    def normalize_identifier(cls, value: str | None) -> str | None:
        """Strip and uppercase a supplied project identifier."""

        return value.strip().upper() if value is not None else None

    @model_validator(mode="after")
    def reject_non_nullable_nulls(self):
        """Allow explicit null only when clearing the description."""

        forbidden = {"name", "identifier", "icon", "color", "access"}
        if any(field in self.model_fields_set and getattr(self, field) is None for field in forbidden):
            raise ValueError("Only description may be cleared with null")
        return self


class ArchiveProjectRequest(APIModel):
    """Exact-name confirmation required to archive a project."""

    confirmation_name: str


class RestoreProjectRequest(APIModel):
    """Empty payload accepted by the project restore command."""

    pass


class ProjectListQueries(APIModel):
    """Validated filters, sorting, and paging for project lists."""

    search: str | None = None
    status: enum.ProjectStatus = enum.ProjectStatus.ACTIVE
    mine: bool = False
    sort: str = Field(default="name", pattern=r"^(name|-name|created_at|-created_at)$")
    cursor: str | None = None
    limit: int = Field(default=30, ge=1, le=100)
