from uuid import UUID

from pydantic import Field

from libs.cp_common.models.pydantic import NoneValidationMixin
from libs.cp_postgresql.models.sqlalchemy import OrmModel, UUIDModel
from models import enum


class ProjectStateDTO(OrmModel):
    """Internal representation of a persisted workflow state."""

    id: UUID
    project_id: UUID
    name: str
    color: str
    group: enum.StateGroup
    position: int
    is_default: bool
    version: int


class ProjectStateCreateDTO(UUIDModel):
    """Fields used to create a project workflow state."""

    project_id: UUID
    name: str
    color: str
    group: enum.StateGroup
    position: int = Field(ge=0)
    is_default: bool = False


class ProjectStateUpdateFieldsDTO(NoneValidationMixin):
    """Optional fields used to update a workflow state."""

    name: str | None = None
    color: str | None = None
    group: enum.StateGroup | None = None
    position: int | None = Field(default=None, ge=0)
    is_default: bool | None = None
    version: int | None = Field(default=None, ge=1)
