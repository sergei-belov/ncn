from datetime import date, datetime
from uuid import UUID

from pydantic import Field

from libs.cp_common.models.pydantic import NoneValidationMixin
from libs.cp_postgresql.models.sqlalchemy import OrmModel, UUIDModel
from models import enum


class EpicDTO(OrmModel):
    """Internal representation of a persisted epic."""

    id: UUID
    project_id: UUID
    sequence_id: int
    title: str
    description_html: str
    state_id: UUID
    priority: enum.Priority
    start_date: date | None
    due_date: date | None
    rank: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    version: int


class EpicCreateDTO(UUIDModel):
    """Fields used to persist a new epic."""

    project_id: UUID
    sequence_id: int = Field(ge=1)
    title: str
    description_html: str = ""
    state_id: UUID
    priority: enum.Priority = enum.Priority.NONE
    start_date: date | None = None
    due_date: date | None = None
    rank: str
    created_by: UUID


class EpicUpdateFieldsDTO(NoneValidationMixin):
    """Optional fields used to update an epic."""

    title: str | None = None
    description_html: str | None = None
    state_id: UUID | None = None
    priority: enum.Priority | None = None
    start_date: date | None = None
    due_date: date | None = None
    rank: str | None = None
    version: int | None = Field(default=None, ge=1)

    _none_allowed_fields = {"start_date", "due_date"}


class EpicAssigneeDTO(OrmModel):
    """Internal representation of an epic-to-user assignment."""

    id: UUID
    epic_id: UUID
    user_id: UUID


class EpicAssigneeCreateDTO(UUIDModel):
    """Fields used to create an epic assignee relation."""

    epic_id: UUID
    user_id: UUID


class EpicAssigneeUpdateFieldsDTO(NoneValidationMixin):
    """Optional fields used to update an epic assignee relation."""

    user_id: UUID | None = None
