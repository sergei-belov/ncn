from datetime import datetime
from uuid import UUID

from libs.cp_common.models.pydantic import NoneValidationMixin
from libs.cp_postgresql.models.sqlalchemy import OrmModel, UUIDModel
from models import enum


class ProjectUserDTO(OrmModel):
    """Internal representation of a user's project membership."""

    id: UUID
    project_id: UUID
    workspace_id: str
    user_id: UUID
    role: enum.ProjectRole
    source: enum.ProjectMembershipSource
    version: int
    created_at: datetime
    updated_at: datetime


class ProjectUserCreateDTO(UUIDModel):
    """Fields used to create a project membership."""

    project_id: UUID
    workspace_id: str
    user_id: UUID
    role: enum.ProjectRole
    source: enum.ProjectMembershipSource = enum.ProjectMembershipSource.MANUAL
    version: int = 1


class ProjectUserUpdateFieldsDTO(NoneValidationMixin):
    """Optional fields used to update a project membership."""

    role: enum.ProjectRole | None = None
    version: int | None = None


class ProjectUserDetailsDTO(ProjectUserDTO):
    """Project membership enriched with user display details."""

    display_name: str
    email: str
    avatar_url: str | None = None
    is_active: bool
