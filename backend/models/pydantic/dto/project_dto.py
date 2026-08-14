from datetime import datetime
from uuid import UUID

from pydantic import Field

from libs.cp_common.models.pydantic import NoneValidationMixin
from libs.cp_postgresql.models.sqlalchemy import OrmModel, UUIDModel
from models import enum


class ProjectDTO(OrmModel):
    """Internal representation of a persisted project."""

    id: UUID
    workspace_slug: str
    name: str
    identifier: str
    description: str | None
    icon: dict
    color: str
    access: enum.ProjectAccess
    default_state_id: UUID | None
    archived_at: datetime | None
    board_version: int
    next_work_item_sequence: int
    next_epic_sequence: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    version: int


class ProjectCreateDTO(UUIDModel):
    """Fields used to create a project."""

    workspace_slug: str
    name: str
    identifier: str
    description: str | None = None
    icon: dict
    color: str
    access: enum.ProjectAccess
    created_by: UUID


class ProjectUpdateFieldsDTO(NoneValidationMixin):
    """Optional fields used to update project state and metadata."""

    name: str | None = None
    identifier: str | None = None
    description: str | None = None
    icon: dict | None = None
    color: str | None = None
    access: enum.ProjectAccess | None = None
    default_state_id: UUID | None = None
    archived_at: datetime | None = None
    board_version: int | None = Field(default=None, ge=1)
    next_work_item_sequence: int | None = Field(default=None, ge=1)
    next_epic_sequence: int | None = Field(default=None, ge=1)
    version: int | None = Field(default=None, ge=1)

    _none_allowed_fields = {"description", "default_state_id", "archived_at"}

