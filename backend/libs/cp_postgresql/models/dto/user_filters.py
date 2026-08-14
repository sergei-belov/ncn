from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
)

from libs.cp_postgresql.models.pydantic.filters import BaseFilter
from libs.cp_postgresql.models.sqlalchemy.uuid_model import UUIDModel


class TableFiltersAggregatedDataDTO(UUIDModel, BaseFilter):
    """Persisted table filter combined with its generated identifier."""

    pass


class TableFiltersDTO(BaseModel):
    """User filters grouped by project and table."""

    project_id: UUID
    user_id: UUID
    table: str
    data: list[TableFiltersAggregatedDataDTO] = Field(default_factory=list)


class CreateTableFilterDTO(UUIDModel):
    """Fields used to create a persisted user table filter."""

    project_id: UUID
    user_id: UUID
    table: str
    filter: BaseFilter


class UpdateTableFilterDTO(BaseModel):
    """Replacement filter used to update a persisted table filter."""

    filter: BaseFilter


class TableFilterDTO(CreateTableFilterDTO):
    """Complete persisted user table filter."""

    pass
