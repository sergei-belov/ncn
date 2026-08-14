from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
)

from libs.cp_postgresql.models import enum
from libs.cp_postgresql.models.sqlalchemy import UUIDModel


class TableRowsDTO(BaseModel):
    """User preference for table row height."""

    height: enum.TableRowHeight = enum.TableRowHeight.MEDIUM


class TableColumnWidthDTO(BaseModel):
    """User-selected width for one table column."""

    column_name: str
    width: int


class TableColumnsDTO(BaseModel):
    """User preferences for table column layout."""

    order: list[str] = Field(default_factory=list)
    hidden: list[str] = Field(default_factory=list)
    pinned: list[str] = Field(default_factory=list)
    width: list[TableColumnWidthDTO] = Field(default_factory=list)


class UpdateTableColumnsDTO(TableColumnsDTO):
    """Optional table column layout fields used for updates."""

    order: list[str] | None = None
    hidden: list[str] | None = None
    pinned: list[str] | None = None
    width: list[TableColumnWidthDTO] | None = None


class TableMetaDTO(BaseModel):
    """Combined row and column preferences for a table."""

    rows: TableRowsDTO = Field(default_factory=TableRowsDTO)
    columns: TableColumnsDTO = Field(default_factory=TableColumnsDTO)


class UserTableMetaDTO(UUIDModel):
    """Persisted table preferences scoped to a project user."""

    project_id: UUID
    user_id: UUID
    table_name: str
    meta: TableMetaDTO = Field(default_factory=TableMetaDTO)
