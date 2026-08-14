from datetime import date, datetime
from uuid import UUID

from pydantic import Field

from libs.cp_common.models.pydantic import NoneValidationMixin
from libs.cp_postgresql.models.sqlalchemy import OrmModel, UUIDModel
from models import enum


class WorkItemDTO(OrmModel):
    """Internal representation of a persisted work item."""

    id: UUID
    project_id: UUID
    sequence_id: int
    title: str
    description_html: str
    state_id: UUID
    priority: enum.Priority
    epic_id: UUID | None
    start_date: date | None
    due_date: date | None
    rank: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    version: int


class WorkItemCreateDTO(UUIDModel):
    """Fields used to persist a new work item."""

    project_id: UUID
    sequence_id: int = Field(ge=1)
    title: str
    description_html: str = ""
    state_id: UUID
    priority: enum.Priority = enum.Priority.NONE
    epic_id: UUID | None = None
    start_date: date | None = None
    due_date: date | None = None
    rank: str
    created_by: UUID


class WorkItemUpdateFieldsDTO(NoneValidationMixin):
    """Optional fields used to update a work item."""

    title: str | None = None
    description_html: str | None = None
    state_id: UUID | None = None
    priority: enum.Priority | None = None
    epic_id: UUID | None = None
    start_date: date | None = None
    due_date: date | None = None
    rank: str | None = None
    version: int | None = Field(default=None, ge=1)

    _none_allowed_fields = {"epic_id", "start_date", "due_date"}


class WorkItemAssigneeDTO(OrmModel):
    """Internal representation of a work-item-to-user assignment."""

    id: UUID
    work_item_id: UUID
    user_id: UUID


class WorkItemAssigneeCreateDTO(UUIDModel):
    """Fields used to create a work-item assignee relation."""

    work_item_id: UUID
    user_id: UUID


class WorkItemAssigneeUpdateFieldsDTO(NoneValidationMixin):
    """Optional fields used to update a work-item assignee relation."""

    user_id: UUID | None = None
