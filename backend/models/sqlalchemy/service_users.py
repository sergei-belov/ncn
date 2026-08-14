from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy import SQLAlchemyBase


class ServiceUser(SQLAlchemyBase):
    """Persist an optional service-role restriction for a project member."""

    __tablename__ = "service_users"

    project_user_id: Mapped[UUID] = sa.Column(
        sa.UUID(as_uuid=False),
        sa.ForeignKey("project_users.id", ondelete="CASCADE", deferrable=True),
        nullable=False,
        index=True,
    )
    service_id: Mapped[str] = sa.Column(sa.String(100), nullable=False)
    role: Mapped[str] = sa.Column(sa.String(16), nullable=False)
    version: Mapped[int] = sa.Column(sa.Integer, nullable=False, server_default="1")
    created_at: Mapped[datetime] = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "project_user_id", "service_id", name="uq_service_users_project_user_service"
        ),
        sa.CheckConstraint("role IN ('admin', 'member', 'viewer')", name="ck_service_users_role"),
        sa.CheckConstraint("version > 0", name="ck_service_users_version_positive"),
    )
