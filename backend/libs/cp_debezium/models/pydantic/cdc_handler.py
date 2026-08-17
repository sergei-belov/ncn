from typing import Type

from cp_postgresql.models.sqlalchemy import (
    SQLAlchemyBase,
    UUIDModel,
)
from pydantic import (
    BaseModel,
    Field,
)

from libs.cp_debezium.models import enum


class BaseDebeziumCDCSourceModel(BaseModel):
    ts_ms: int


class BaseDebeziumCDCModel(BaseModel):
    before: dict | None
    after: dict | None
    op: enum.DebeziumCDCType
    source: BaseDebeziumCDCSourceModel


class DeleteDebeziumCDCModel(UUIDModel):
    pass


class DebeziumSinkCDC(BaseModel):
    sql_model: Type[SQLAlchemyBase]
    dto_model: Type[UUIDModel]
    topic: str
    batch_size: int = 1
    exclude_fields: set[str] = Field(default_factory=set)
