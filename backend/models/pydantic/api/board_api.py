from uuid import UUID

from pydantic import Field, model_validator

from models import enum
from models.pydantic.api.common_api import APIModel, CursorMeta, MemberSummary, ProjectPermissions
from models.pydantic.api.epic_api import EpicPickerItem
from models.pydantic.api.project_api import Project
from models.pydantic.api.state_api import State
from models.pydantic.api.work_item_api import WorkItemCard


class BoardDisplayProperties(APIModel):
    """Boolean controls for optional information displayed on board cards."""

    show_priority: bool = True
    show_assignees: bool = True
    show_due_date: bool = True
    show_epic: bool = True


class BoardPreferences(APIModel):
    """Public user-specific preferences for a project board."""

    display: BoardDisplayProperties
    collapsed_state_ids: list[UUID]
    version: int


class BoardPreferencesResponse(APIModel):
    """Response envelope containing board preferences."""

    data: BoardPreferences
    meta: dict | None = None


class UpdateBoardPreferencesRequest(APIModel):
    """Validated partial update for board preferences."""

    display: dict[str, bool] | None = None
    collapsed_state_ids: list[UUID] | None = None

    @model_validator(mode="after")
    def reject_nulls(self):
        """Reject explicit null values for supplied preference fields."""

        if any(field in self.model_fields_set and getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Board preference fields cannot be null")
        return self


class BoardColumnSnapshot(APIModel):
    """One workflow state and its visible page of work-item cards."""

    state: State
    work_items: list[WorkItemCard]
    page: CursorMeta


class BoardIncluded(APIModel):
    """Lookup entities included alongside a board snapshot."""

    members: list[MemberSummary]
    epics: list[EpicPickerItem]


class BoardSnapshot(APIModel):
    """Complete frontend-facing read model for a project board."""

    project: Project
    permissions: ProjectPermissions
    board_version: int
    columns: list[BoardColumnSnapshot]
    included: BoardIncluded
    preferences: BoardPreferences


class BoardResponse(APIModel):
    """Response envelope containing a project board snapshot."""

    data: BoardSnapshot
    meta: dict | None = None


class BoardQueries(APIModel):
    """Validated filtering and per-column paging options for a board."""

    search: str | None = None
    priority: str | None = None
    assignee_id: str | None = None
    epic_id: str | None = None
    due_status: enum.DueStatus | None = None
    only_mine: bool = False
    per_column: int = Field(default=30, ge=1, le=50)
