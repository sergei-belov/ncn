from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy import SQLAlchemyBase


class UserFilter(SQLAlchemyBase):
    """Abstract table shape for persisted user filters."""

    __tablename__ = "user_filters"
    __abstract__ = True

    created_at: Mapped[datetime] = sa.Column(sa.DateTime, server_default=sa.func.now())
    project_id: Mapped[sa.UUID] = sa.Column(sa.UUID(as_uuid=False), nullable=False, index=True)
    user_id: Mapped[sa.UUID] = sa.Column(sa.UUID(as_uuid=False), nullable=False, index=True)
    table: Mapped[str] = sa.Column(sa.String(50), nullable=False, index=True)
    filter: Mapped[dict] = sa.Column(JSONB, nullable=False)
