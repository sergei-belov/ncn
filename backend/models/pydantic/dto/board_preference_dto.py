from uuid import UUID

from pydantic import Field

from libs.cp_common.models.pydantic import NoneValidationMixin
from libs.cp_postgresql.models.sqlalchemy import OrmModel, UUIDModel


class BoardPreferenceDTO(OrmModel):
    """Internal representation of persisted user board preferences."""

    id: UUID
    project_id: UUID
    user_id: UUID
    display: dict
    collapsed_state_ids: list[UUID]
    version: int


class BoardPreferenceCreateDTO(UUIDModel):
    """Fields used to initialize a user's board preferences."""

    project_id: UUID
    user_id: UUID
    display: dict = Field(default_factory=dict)
    collapsed_state_ids: list[UUID] = Field(default_factory=list)


class BoardPreferenceUpdateFieldsDTO(NoneValidationMixin):
    """Optional fields used to update board preferences."""

    display: dict | None = None
    collapsed_state_ids: list[UUID] | None = None
    version: int | None = Field(default=None, ge=1)
