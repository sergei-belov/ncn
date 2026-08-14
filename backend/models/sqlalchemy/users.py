# models/sqlalchemy/users.py
from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy import SQLAlchemyBase


class User(SQLAlchemyBase):
    """Persist a stable application user and optional local credential hash."""

    __tablename__ = "users"

    email: Mapped[str] = sa.Column(sa.String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = sa.Column(sa.String(100), nullable=False)
    password_hash: Mapped[str | None] = sa.Column("password", sa.String, nullable=True)
    is_active: Mapped[bool] = sa.Column(sa.Boolean, nullable=False, server_default=sa.true())
    created_at: Mapped[datetime] = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )

    __table_args__ = (
        sa.CheckConstraint("email = lower(btrim(email))", name="ck_users_email_canonical"),
        sa.CheckConstraint("is_active IN (true, false)", name="ck_users_is_active"),
    )
