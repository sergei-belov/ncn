from datetime import date, datetime
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from models import enum
from models.pydantic.api.common_api import APIModel, CursorMeta, MemberSummary, ProjectPermissions
from models.pydantic.api.entity_api import EpicPickerItem, WorkItemCard
from models.pydantic.api.state_api import State


class EpicListItem(APIModel):
    """Epic summary enriched with assignees and progress aggregates."""

    id: UUID
    project_id: UUID
    sequence_id: int
    identifier: str
    title: str
    state_id: UUID
    priority: enum.Priority
    assignee_ids: list[UUID]
    start_date: date | None
    due_date: date | None
    rank: str
    work_items_count: int
    completed_work_items_count: int
    progress_percent: int = Field(ge=0, le=100)
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    version: int


class Epic(EpicListItem):
    """Complete epic representation including sanitized rich text."""

    description_html: str


class EpicResponse(APIModel):
    """Response envelope containing one complete epic."""

    data: Epic
    meta: dict | None = None


class EpicPage(APIModel):
    """Cursor-paginated response containing epic summaries."""

    data: list[EpicListItem]
    meta: CursorMeta


class EpicMutationFields(APIModel):
    """Fields shared by epic creation and partial updates."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description_html: str | None = None
    state_id: UUID | None = None
    priority: enum.Priority | None = None
    assignee_ids: list[UUID] | None = Field(default=None, max_length=10)
    start_date: date | None = None
    due_date: date | None = None

    @field_validator("title")
    @classmethod
    def trim_title(cls, value: str | None) -> str | None:
        """Strip a supplied epic title and reject blank content."""

        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("title must not be blank")
        return value

    @model_validator(mode="after")
    def validate_dates(self):
        """Require the start date to be no later than the due date."""

        if self.start_date and self.due_date and self.start_date > self.due_date:
            raise ValueError("start_date must be before or equal to due_date")
        return self


class CreateEpicRequest(EpicMutationFields):
    """Validated idempotent epic creation payload."""

    id: UUID = Field(description="Client-generated epic and idempotency identifier")
    title: str = Field(min_length=1, max_length=255)

    @model_validator(mode="after")
    def reject_non_nullable_nulls(self):
        """Allow explicit null only for optional epic dates."""

        forbidden = {"title", "description_html", "state_id", "priority", "assignee_ids"}
        if any(field in self.model_fields_set and getattr(self, field) is None for field in forbidden):
            raise ValueError("Only dates may be null")
        return self


class UpdateEpicRequest(EpicMutationFields):
    """Validated partial epic update payload."""

    @model_validator(mode="after")
    def reject_non_nullable_nulls(self):
        """Allow explicit null only when clearing optional epic dates."""

        forbidden = {"title", "description_html", "state_id", "priority", "assignee_ids"}
        if any(field in self.model_fields_set and getattr(self, field) is None for field in forbidden):
            raise ValueError("Only dates may be cleared with null")
        return self


class EpicListQueries(APIModel):
    """Validated filters, sorting, and paging for epic lists."""

    search: str | None = None
    state_group: str | None = None
    priority: str | None = None
    assignee_id: str | None = None
    status: enum.EpicStatus | None = None
    sort: str = Field(default="rank", pattern=r"^(rank|created_at|-created_at|due_date|-progress)$")
    cursor: str | None = None
    limit: int = Field(default=30, ge=1, le=100)


class EpicIncluded(APIModel):
    """Lookup entities included with detailed epic responses."""

    states: list[State]
    members: list[MemberSummary]


class EpicDetailData(APIModel):
    """Detailed epic, lookup entities, and actor permissions."""

    epic: Epic
    included: EpicIncluded
    permissions: ProjectPermissions


class EpicDetailResponse(APIModel):
    """Response envelope containing detailed epic data."""

    data: EpicDetailData
    meta: dict | None = None


class AddEpicWorkItemsRequest(APIModel):
    """Payload for attaching work items to an epic."""

    work_item_ids: list[UUID] = Field(min_length=1, max_length=100)
    move_from_other_epics: bool


class EpicWorkItemsMutationData(APIModel):
    """Refreshed epic and work-item cards after membership changes."""

    epic: EpicListItem
    updated_work_items: list[WorkItemCard]


class EpicWorkItemsMutationResponse(APIModel):
    """Response envelope for epic work-item membership changes."""

    data: EpicWorkItemsMutationData
    meta: dict | None = None
