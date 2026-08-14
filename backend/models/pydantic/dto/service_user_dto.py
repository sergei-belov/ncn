from datetime import datetime
from uuid import UUID

from libs.cp_common.models.pydantic import NoneValidationMixin
from libs.cp_postgresql.models.sqlalchemy import OrmModel, UUIDModel
from models import enum


class ServiceUserDTO(OrmModel):
    """Internal representation of a project-service restriction."""

    id: UUID
    project_user_id: UUID
    service_id: str
    role: enum.ProjectRole
    version: int
    created_at: datetime
    updated_at: datetime


class ServiceUserCreateDTO(UUIDModel):
    """Fields used to create a project-service restriction."""

    project_user_id: UUID
    service_id: str
    role: enum.ProjectRole
    version: int = 1


class ServiceUserUpdateFieldsDTO(NoneValidationMixin):
    """Optional fields used to update a project-service restriction."""

    role: enum.ProjectRole | None = None
    version: int | None = None
