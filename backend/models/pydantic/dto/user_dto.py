from datetime import datetime
from uuid import UUID

from libs.cp_common.models.pydantic import NoneValidationMixin
from libs.cp_postgresql.models.sqlalchemy import OrmModel, UUIDModel
from models import enum


class UserDTO(OrmModel):
    """Internal representation of an application user."""

    id: UUID
    email: str
    name: str
    password: str | None
    created_at: datetime


class UserCreateDTO(UUIDModel):
    """Fields used to create an application user."""

    email: str
    name: str
    password: str | None = None


class UserWithPasswordDTO(UserCreateDTO):
    """User creation fields requiring a password value."""

    password: str


class UserUpdateFieldsDTO(NoneValidationMixin):
    """Optional fields used to update an application user."""

    name: str | None = None
    password: str | None = None

    _none_allowed_fields = {"password"}


class UserAccessDataDTO(UserDTO):
    """User data with an optional project authorization relation."""

    project_user_id: UUID | None
    project_id: UUID | None
    workspace_slug: str | None
    project_role: enum.ProjectRole | None


class UserAuthorizedDTO(UserDTO):
    """User data with a required project authorization relation."""

    project_user_id: UUID
    project_id: UUID
    workspace_slug: str
    project_role: enum.ProjectRole
