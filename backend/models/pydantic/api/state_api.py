from uuid import UUID

from pydantic import Field, field_validator, model_validator

from models import enum
from models.pydantic.api.common_api import APIModel


class State(APIModel):
    """Public workflow state with its current work-item count."""

    id: UUID
    project_id: UUID
    name: str
    color: str
    group: enum.StateGroup
    position: int
    is_default: bool
    work_items_count: int = 0
    version: int


class StateResponse(APIModel):
    """Response envelope containing one workflow state."""

    data: State
    meta: dict | None = None


class StateListResponse(APIModel):
    """Response envelope containing ordered workflow states."""

    data: list[State]
    meta: dict | None = None


class CreateStateRequest(APIModel):
    """Validated idempotent workflow-state creation payload."""

    id: UUID = Field(description="Client-generated state and idempotency identifier")
    name: str = Field(min_length=1, max_length=50)
    color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    group: enum.StateGroup
    after_state_id: UUID | None = None
    is_default: bool = False

    @field_validator("name")
    @classmethod
    def trim_name(cls, value: str) -> str:
        """Strip a state name and reject blank content."""

        value = value.strip()
        if not value:
            raise ValueError("name must not be blank")
        return value


class UpdateStateRequest(APIModel):
    """Validated partial workflow-state update payload."""

    name: str | None = Field(default=None, min_length=1, max_length=50)
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    group: enum.StateGroup | None = None
    is_default: bool | None = None

    @field_validator("name")
    @classmethod
    def trim_name(cls, value: str | None) -> str | None:
        """Strip a supplied state name and reject blank content."""

        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("name must not be blank")
        return value

    @model_validator(mode="after")
    def reject_nulls(self):
        """Reject explicit null values for every state update field."""

        if any(field in self.model_fields_set and getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("State fields cannot be null")
        return self


class ReorderStatesRequest(APIModel):
    """Complete state order with the expected project board version."""

    ordered_state_ids: list[UUID] = Field(min_length=1)
    expected_board_version: int = Field(ge=1)


class ReorderStatesData(APIModel):
    """Reordered states paired with the resulting board version."""

    states: list[State]
    board_version: int


class ReorderStatesResponse(APIModel):
    """Response envelope for a workflow-state reorder operation."""

    data: ReorderStatesData
    meta: dict | None = None
