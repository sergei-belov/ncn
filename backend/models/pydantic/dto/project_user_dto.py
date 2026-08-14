from uuid import UUID

from libs.cp_common.models.pydantic import NoneValidationMixin
from libs.cp_postgresql.models.sqlalchemy import OrmModel, UUIDModel
from models import enum


class ProjectUserDTO(OrmModel):
    """Internal representation of a user's project membership."""

    id: UUID
    project_id: UUID
    user_id: UUID
    role: enum.ProjectRole


class ProjectUserCreateDTO(UUIDModel):
    """Fields used to create a project membership."""

    project_id: UUID
    user_id: UUID
    role: enum.ProjectRole


class ProjectUserUpdateFieldsDTO(NoneValidationMixin):
    """Optional fields used to update a project membership."""

    role: enum.ProjectRole | None = None


class ProjectUserDetailsDTO(ProjectUserDTO):
    """Project membership enriched with user display details."""

    display_name: str
    avatar_url: str | None = None
    is_active: bool = True
