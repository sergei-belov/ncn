from datetime import date, datetime
from uuid import UUID

from models import enum
from models.pydantic.api.common_api import APIModel


class WorkItemCard(APIModel):
    """Compact work-item representation used in lists and board columns."""

    id: UUID
    project_id: UUID
    sequence_id: int
    identifier: str
    title: str
    state_id: UUID
    priority: enum.Priority
    assignee_ids: list[UUID]
    epic_id: UUID | None
    start_date: date | None
    due_date: date | None
    rank: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    version: int


class EpicPickerItem(APIModel):
    """Compact epic representation used by work-item selection controls."""

    id: UUID
    identifier: str
    title: str
    state_id: UUID
    progress_percent: int
