from datetime import datetime
from uuid import UUID

from libs.cp_common.models.pydantic import NoneValidationMixin
from libs.cp_postgresql.models.sqlalchemy import OrmModel, UUIDModel
from models import enum


class WorkspaceUserDTO(OrmModel):
    """Internal representation of a workspace membership."""

    id: UUID
    workspace_id: str
    user_id: UUID
    role: enum.WorkspaceRole
    version: int
    created_at: datetime
    updated_at: datetime


class WorkspaceUserCreateDTO(UUIDModel):
    """Fields used to create a workspace membership."""

    workspace_id: str
    user_id: UUID
    role: enum.WorkspaceRole
    version: int = 1


class WorkspaceUserUpdateFieldsDTO(NoneValidationMixin):
    """Optional fields used to update a workspace membership."""

    role: enum.WorkspaceRole | None = None
    version: int | None = None


class WorkspaceUserDetailsDTO(WorkspaceUserDTO):
    """Workspace membership enriched with safe user display fields."""

    email: str
    name: str
    is_active: bool
