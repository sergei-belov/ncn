from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy import SQLAlchemyBase


class ProjectUser(SQLAlchemyBase):
    """Persist one user's role in an externally owned project."""

    __tablename__ = "project_users"

    project_id: Mapped[UUID] = sa.Column(
        sa.UUID(as_uuid=False),
        nullable=False,
        index=True,
    )
    workspace_id: Mapped[str] = sa.Column(sa.String(100), nullable=False, index=True)
    user_id: Mapped[UUID] = sa.Column(
        sa.UUID(as_uuid=False),
        sa.ForeignKey("users.id", ondelete="CASCADE", deferrable=True),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = sa.Column(sa.String(16), nullable=False)
    source: Mapped[str] = sa.Column(sa.String(16), nullable=False, server_default="manual")
    version: Mapped[int] = sa.Column(sa.Integer, nullable=False, server_default="1")
    created_at: Mapped[datetime] = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )

    __table_args__ = (
        sa.UniqueConstraint("project_id", "user_id", name="uq_project_users_project_user"),
        sa.CheckConstraint("role IN ('admin', 'member', 'viewer')", name="ck_project_users_role"),
        sa.CheckConstraint("source IN ('manual', 'bootstrap')", name="ck_project_users_source"),
        sa.CheckConstraint("version > 0", name="ck_project_users_version_positive"),
    )
