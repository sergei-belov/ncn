# models/sqlalchemy/users.py
from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy import SQLAlchemyBase


class User(SQLAlchemyBase):
    """Application user."""

    __tablename__ = "users"

    email: Mapped[str] = sa.Column(sa.String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = sa.Column(sa.String(100), nullable=False)
    password: Mapped[str | None] = sa.Column(sa.String, nullable=True)
    created_at: Mapped[datetime] = sa.Column(sa.DateTime(), nullable=False, server_default=sa.func.now())
