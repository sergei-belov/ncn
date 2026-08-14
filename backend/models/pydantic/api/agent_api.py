from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from models import enum
from models.pydantic.api.common_api import APIModel


class Agent(APIModel):
    """Public representation of a configured project agent."""

    id: UUID
    project_id: UUID
    kind: enum.AgentKind
    name: str
    description: str
    instructions: str
    model: str
    memory_policy: enum.AgentMemoryPolicy
    max_steps_per_run: int = Field(ge=1)
    approval_mode: enum.AgentApprovalMode
    status: enum.AgentStatus
    system_tool_names: list[str]
    created_at: datetime
    updated_at: datetime
    version: int = Field(ge=1)


class AgentResponse(APIModel):
    """Response envelope containing one project agent."""

    data: Agent


class AgentListResponse(APIModel):
    """Response envelope containing project agents."""

    data: list[Agent]


class CreateAgentRequest(APIModel):
    """Validated payload for creating a worker agent."""

    name: str = Field(min_length=2, max_length=80)
    description: str = Field(max_length=240)
    instructions: str = Field(min_length=20, max_length=4000)
    model: str = Field(min_length=1, max_length=255)
    memory_policy: enum.AgentMemoryPolicy
    max_steps_per_run: int = Field(ge=1)
    approval_mode: enum.AgentApprovalMode

    @field_validator("name", "description", "instructions", "model", mode="before")
    @classmethod
    def trim_text(cls, value: str) -> str:
        """Strip surrounding whitespace from textual agent configuration."""

        return value.strip() if isinstance(value, str) else value


class UpdateAgentRequest(APIModel):
    """Validated partial agent update with an expected version."""

    expected_version: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=240)
    instructions: str | None = Field(default=None, min_length=20, max_length=4000)
    model: str | None = Field(default=None, min_length=1, max_length=255)
    memory_policy: enum.AgentMemoryPolicy | None = None
    max_steps_per_run: int | None = Field(default=None, ge=1)
    approval_mode: enum.AgentApprovalMode | None = None

    @field_validator("name", "description", "instructions", "model", mode="before")
    @classmethod
    def trim_text(cls, value: str | None) -> str | None:
        """Strip surrounding whitespace from supplied text fields."""

        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def reject_nulls(self):
        """Reject explicit null values for every updateable agent field."""

        if any(
            field in self.model_fields_set and getattr(self, field) is None
            for field in self.__class__.model_fields
        ):
            raise ValueError("Agent configuration fields cannot be null")
        return self


class AgentCommandRequest(APIModel):
    """Optimistic concurrency payload for an agent lifecycle command."""

    expected_version: int = Field(ge=1)
