from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy import SQLAlchemyBase


class WorkspaceUser(SQLAlchemyBase):
    """Persist one user's role in an externally owned workspace."""

    __tablename__ = "workspace_users"

    workspace_id: Mapped[str] = sa.Column(sa.String(100), nullable=False, index=True)
    user_id: Mapped[UUID] = sa.Column(
        sa.UUID(as_uuid=False),
        sa.ForeignKey("users.id", ondelete="CASCADE", deferrable=True),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = sa.Column(sa.String(16), nullable=False)
    version: Mapped[int] = sa.Column(sa.Integer, nullable=False, server_default="1")
    created_at: Mapped[datetime] = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )

    __table_args__ = (
        sa.UniqueConstraint("workspace_id", "user_id", name="uq_workspace_users_workspace_user"),
        sa.CheckConstraint("role IN ('owner', 'admin', 'member')", name="ck_workspace_users_role"),
        sa.CheckConstraint("version > 0", name="ck_workspace_users_version_positive"),
    )
