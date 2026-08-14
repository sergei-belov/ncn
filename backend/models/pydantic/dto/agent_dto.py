from datetime import datetime
from uuid import UUID

from pydantic import Field

from libs.cp_common.models.pydantic import NoneValidationMixin
from libs.cp_postgresql.models.sqlalchemy import OrmModel, UUIDModel
from models import enum


class AgentDTO(OrmModel):
    """Internal representation of a persisted project agent."""

    id: UUID
    project_id: UUID
    kind: enum.AgentKind
    name: str
    description: str
    instructions: str
    model: str
    memory_policy: enum.AgentMemoryPolicy
    max_steps_per_run: int
    approval_mode: enum.AgentApprovalMode
    status: enum.AgentStatus
    system_tool_names: list[str]
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    version: int


class AgentCreateDTO(UUIDModel):
    """Validated fields used to create a project agent."""

    project_id: UUID
    kind: enum.AgentKind
    name: str = Field(min_length=2, max_length=80)
    description: str = Field(max_length=240)
    instructions: str = Field(min_length=20, max_length=4000)
    model: str = Field(min_length=1, max_length=255)
    memory_policy: enum.AgentMemoryPolicy
    max_steps_per_run: int = Field(ge=1)
    approval_mode: enum.AgentApprovalMode
    status: enum.AgentStatus = enum.AgentStatus.ACTIVE
    system_tool_names: list[str] = Field(default_factory=list)
    created_by: UUID


class AgentUpdateFieldsDTO(NoneValidationMixin):
    """Validated optional fields used to update an agent."""

    name: str | None = Field(default=None, min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=240)
    instructions: str | None = Field(default=None, min_length=20, max_length=4000)
    model: str | None = Field(default=None, min_length=1, max_length=255)
    memory_policy: enum.AgentMemoryPolicy | None = None
    max_steps_per_run: int | None = Field(default=None, ge=1)
    approval_mode: enum.AgentApprovalMode | None = None
    status: enum.AgentStatus | None = None
    version: int | None = Field(default=None, ge=1)
