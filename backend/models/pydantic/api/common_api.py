from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")


class APIModel(BaseModel):
    """Base API model with strict fields and attribute-based validation."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)


class DataResponse(APIModel, Generic[T]):
    """Generic response envelope containing one data value."""

    data: T
    meta: dict | None = None


class CursorMeta(APIModel):
    """Cursor pagination metadata returned with collection responses."""

    next_cursor: str | None = None
    has_more: bool = False
    total_count: int = Field(ge=0)


class CursorPage(APIModel, Generic[T]):
    """Generic cursor-paginated collection response."""

    data: list[T]
    meta: CursorMeta


class FieldError(APIModel):
    """Machine-readable validation failure for one field."""

    code: str
    message: str


class ErrorDetail(APIModel):
    """Structured error details exposed by the public API."""

    code: str
    message: str
    correlation_id: str | None = None
    field_errors: dict[str, list[FieldError]] | None = None
    details: dict | None = None
    current: dict | None = None


class ApiError(APIModel):
    """Top-level public API error envelope."""

    error: ErrorDetail


class IconValue(APIModel):
    """Validated emoji or initial used as an entity icon."""

    type: str = Field(pattern="^(emoji|initial)$")
    value: str = Field(min_length=1, max_length=16)


class MemberSummary(APIModel):
    """Compact project-member representation for previews and pickers."""

    id: UUID
    display_name: str
    avatar_url: str | None = None
    is_active: bool


class ProjectPermissions(APIModel):
    """Explicit capabilities granted to an actor within a project."""

    can_view_project: bool
    can_edit_project: bool
    can_archive_project: bool
    can_manage_states: bool
    can_manage_agents: bool
    can_create_work_item: bool
    can_edit_work_item: bool
    can_move_work_item: bool
    can_delete_own_work_item: bool
    can_delete_any_work_item: bool
    can_create_epic: bool
    can_edit_epic: bool
    can_delete_own_epic: bool
    can_delete_any_epic: bool


class WorkspaceProjectPermissions(APIModel):
    """Workspace-scoped capabilities related to projects."""

    can_create_project: bool


class EntityAudit(APIModel):
    """Common creation, update, and version fields for public entities."""

    created_by: UUID
    created_at: datetime
    updated_at: datetime
    version: int = Field(ge=1)
