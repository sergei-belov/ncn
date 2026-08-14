from datetime import date
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from models import enum
from models.pydantic.api.common_api import APIModel, CursorMeta, MemberSummary, ProjectPermissions
from models.pydantic.api.entity_api import EpicPickerItem, WorkItemCard
from models.pydantic.api.state_api import State


class WorkItem(WorkItemCard):
    """Complete work-item representation including sanitized rich text."""

    description_html: str


class WorkItemResponse(APIModel):
    """Response envelope containing one complete work item."""

    data: WorkItem
    meta: dict | None = None


class WorkItemPage(APIModel):
    """Cursor-paginated response containing work-item cards."""

    data: list[WorkItemCard]
    meta: CursorMeta


class WorkItemMutationFields(APIModel):
    """Fields shared by work-item creation and partial updates."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description_html: str | None = None
    state_id: UUID | None = None
    priority: enum.Priority | None = None
    assignee_ids: list[UUID] | None = Field(default=None, max_length=10)
    epic_id: UUID | None = None
    start_date: date | None = None
    due_date: date | None = None

    @field_validator("title")
    @classmethod
    def trim_title(cls, value: str | None) -> str | None:
        """Strip a supplied work-item title and reject blank content."""

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


class CreateWorkItemRequest(WorkItemMutationFields):
    """Validated idempotent work-item creation payload."""

    id: UUID = Field(description="Client-generated work item and idempotency identifier")
    title: str = Field(min_length=1, max_length=255)
    before_work_item_id: UUID | None = None
    after_work_item_id: UUID | None = None

    @model_validator(mode="after")
    def validate_anchor(self):
        """Require creation to specify at most one ordering anchor."""

        if self.before_work_item_id and self.after_work_item_id:
            raise ValueError("before_work_item_id and after_work_item_id are mutually exclusive")
        return self

    @model_validator(mode="after")
    def reject_non_nullable_nulls(self):
        """Allow explicit null only for epic and date fields."""

        forbidden = {"title", "description_html", "state_id", "priority", "assignee_ids"}
        if any(field in self.model_fields_set and getattr(self, field) is None for field in forbidden):
            raise ValueError("Only epic_id and dates may be null")
        return self


class UpdateWorkItemRequest(WorkItemMutationFields):
    """Validated partial work-item update payload."""

    @model_validator(mode="after")
    def reject_non_nullable_nulls(self):
        """Allow explicit null only when clearing epic or date fields."""

        forbidden = {"title", "description_html", "state_id", "priority", "assignee_ids"}
        if any(field in self.model_fields_set and getattr(self, field) is None for field in forbidden):
            raise ValueError("Only epic_id and dates may be cleared with null")
        return self


class MoveWorkItemRequest(APIModel):
    """Optimistic move command with target state and ordering anchors."""

    to_state_id: UUID
    before_work_item_id: UUID | None = None
    after_work_item_id: UUID | None = None
    expected_work_item_version: int = Field(ge=1)
    expected_board_version: int = Field(ge=1)
    client_mutation_id: UUID


class MoveWorkItemData(APIModel):
    """Canonical result of moving a work item on the board."""

    work_item: WorkItemCard
    board_version: int
    client_mutation_id: UUID
    canonical_before_work_item_id: UUID | None
    canonical_after_work_item_id: UUID | None


class MoveWorkItemResponse(APIModel):
    """Response envelope for a work-item move operation."""

    data: MoveWorkItemData
    meta: dict | None = None


class WorkItemListQueries(APIModel):
    """Validated filters, sorting, and paging for work-item lists."""

    search: str | None = None
    state_id: UUID | None = None
    priority: str | None = None
    assignee_id: str | None = None
    epic_id: str | None = None
    due_status: enum.DueStatus | None = None
    created_by: UUID | None = None
    sort: str = Field(default="rank", pattern=r"^(rank|created_at|-created_at|due_date)$")
    cursor: str | None = None
    limit: int = Field(default=30, ge=1, le=100)


class WorkItemIncluded(APIModel):
    """Lookup entities included with detailed work-item responses."""

    states: list[State]
    members: list[MemberSummary]
    epics: list[EpicPickerItem]


class WorkItemDetailData(APIModel):
    """Detailed work item, lookup entities, and actor permissions."""

    work_item: WorkItem
    included: WorkItemIncluded
    permissions: ProjectPermissions


class WorkItemDetailResponse(APIModel):
    """Response envelope containing detailed work-item data."""

    data: WorkItemDetailData
    meta: dict | None = None
