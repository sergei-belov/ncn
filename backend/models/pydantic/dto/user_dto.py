from datetime import datetime
from uuid import UUID

from libs.cp_common.models.pydantic import NoneValidationMixin
from libs.cp_postgresql.models.sqlalchemy import OrmModel, UUIDModel
from models import enum


def normalize_email(value: str) -> str:
    """Return the canonical email key used by every identity flow.

    Args:
        value: Raw email-like value supplied by an identity boundary.

    Returns:
        The stripped and Unicode case-normalized value.
    """

    return value.strip().casefold()


class UserDTO(OrmModel):
    """Internal representation of an application user."""

    id: UUID
    email: str
    name: str
    password_hash: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserCreateDTO(UUIDModel):
    """Fields used to create an application user."""

    email: str
    name: str
    password_hash: str | None = None
    is_active: bool = True


class UserWithPasswordDTO(UserCreateDTO):
    """User creation fields requiring a password value."""

    password_hash: str


class UserUpdateFieldsDTO(NoneValidationMixin):
    """Optional fields used to update an application user."""

    name: str | None = None
    password_hash: str | None = None
    is_active: bool | None = None

    _none_allowed_fields = {"password_hash"}


class UserAuthorizedDTO(UserDTO):
    """User data with a required project authorization relation."""

    project_user_id: UUID
    project_id: UUID
    workspace_slug: str
    project_role: enum.ProjectRole
