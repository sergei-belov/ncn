from uuid import UUID

from libs.cp_common.models.enum import (
    Service,
    ServiceRole,
)
from libs.cp_common.models.pydantic import NoneValidationMixin
from libs.cp_postgresql.models.sqlalchemy import UUIDModel


class ServiceUserDTO(UUIDModel):
    """Shared representation of service access for a project user."""

    service: Service
    project_user_id: UUID
    role: ServiceRole


class ServiceUserUpdateFieldsDTO(NoneValidationMixin):
    """Optional fields used to update a service-user relation."""

    service: Service | None = None
    role: ServiceRole | None = None
