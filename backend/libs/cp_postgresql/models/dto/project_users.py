from uuid import UUID

from libs.cp_common.models.enum import ProjectRole
from libs.cp_common.models.pydantic import NoneValidationMixin
from libs.cp_postgresql.models.sqlalchemy import UUIDModel


class ProjectUserDTO(UUIDModel):
    """Shared representation of a user's project membership."""

    project_id: UUID
    user_id: UUID
    role: ProjectRole


class ProjectUserUpdateFieldsDTO(NoneValidationMixin):
    """Optional fields used to update project membership."""

    role: ProjectRole | None = None
