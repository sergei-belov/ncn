import uuid

from pydantic import Field

from libs.cp_common.models.pydantic import UUIDSerialized
from libs.cp_postgresql.models.sqlalchemy.orm_model import OrmModel


class UUIDModel(OrmModel):
    """ORM model with automatic UUID generator for `id` field."""

    id: UUIDSerialized = Field(default_factory=uuid.uuid4)
