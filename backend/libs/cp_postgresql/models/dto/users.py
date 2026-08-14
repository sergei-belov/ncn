from uuid import UUID

from libs.cp_common.models.enum import (
    ProjectRole,
    ServiceRole,
)
from libs.cp_common.models.pydantic import NoneValidationMixin
from libs.cp_postgresql.models.sqlalchemy.uuid_model import UUIDModel


class UserDTO(UUIDModel):
    """Shared representation of an application user."""

    email: str
    name: str
    password: str | None = None


class UserWithPasswordDTO(UserDTO):
    """Shared user representation requiring a password."""

    password: str


class UserAccessDataDTO(UserDTO):
    """User enriched with optional project and service authorization."""

    project_user_id: UUID | None
    project_id: UUID | None
    project_name: str | None
    project_description: str | None = None
    project_role: ProjectRole | None
    service_user_id: UUID | None
    service_role: ServiceRole | None


class UserAuthorizedDTO(UserDTO):
    """User enriched with required project and service authorization."""

    project_user_id: UUID
    project_id: UUID
    project_name: str
    project_description: str | None = None
    project_role: ProjectRole
    service_user_id: UUID
    service_role: ServiceRole


class UserUpdateFieldsDTO(NoneValidationMixin):
    """Optional fields used to update a shared user."""

    name: str | None = None
    password: str | None = None

    _none_allowed_fields = {"password"}
