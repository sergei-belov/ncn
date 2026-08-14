import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy import SQLAlchemyBase


class UserTableMeta(SQLAlchemyBase):
    """Abstract table shape for per-user table preferences."""

    __tablename__ = "user_table_meta"
    __abstract__ = True

    project_id: Mapped[sa.UUID] = sa.Column(sa.UUID(as_uuid=False), nullable=False, index=True)
    user_id: Mapped[sa.UUID] = sa.Column(sa.UUID(as_uuid=False), nullable=False, index=True)
    table_name: Mapped[str] = sa.Column(sa.String(50), nullable=False, index=True)
    meta: Mapped[dict] = sa.Column(JSONB, nullable=False, server_default="{}")

    __table_args__ = (sa.UniqueConstraint("project_id", "user_id", "table_name"),)
