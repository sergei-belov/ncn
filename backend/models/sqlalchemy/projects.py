from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy import SQLAlchemyBase


class Project(SQLAlchemyBase):
    """Persist project metadata, sequences, and board concurrency state."""

    __tablename__ = "pms_projects"

    workspace_slug: Mapped[str] = sa.Column(sa.String(100), nullable=False, index=True)
    name: Mapped[str] = sa.Column(sa.String(255), nullable=False)
    identifier: Mapped[str] = sa.Column(sa.String(10), nullable=False)
    description: Mapped[str | None] = sa.Column(sa.Text, nullable=True)
    icon: Mapped[dict] = sa.Column(
        JSONB,
        nullable=False,
        server_default=sa.text("'{\"type\":\"initial\",\"value\":\"P\"}'::jsonb"),
    )
    color: Mapped[str] = sa.Column(sa.String(7), nullable=False, server_default="#5E6AD2")
    access: Mapped[str] = sa.Column(sa.String(16), nullable=False, server_default="private")
    default_state_id: Mapped[UUID | None] = sa.Column(sa.UUID(as_uuid=False), nullable=True)
    archived_at: Mapped[datetime | None] = sa.Column(sa.DateTime(timezone=True), nullable=True, index=True)
    board_version: Mapped[int] = sa.Column(sa.Integer, nullable=False, server_default="1")
    next_work_item_sequence: Mapped[int] = sa.Column(sa.Integer, nullable=False, server_default="1")
    next_epic_sequence: Mapped[int] = sa.Column(sa.Integer, nullable=False, server_default="1")
    created_by: Mapped[UUID] = sa.Column(sa.UUID(as_uuid=False), nullable=False, index=True)
    created_at: Mapped[datetime] = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )
    version: Mapped[int] = sa.Column(sa.Integer, nullable=False, server_default="1")

    __table_args__ = (
        sa.UniqueConstraint("workspace_slug", "identifier", name="uq_pms_projects_workspace_identifier"),
        sa.CheckConstraint("version > 0", name="ck_pms_projects_version_positive"),
        sa.CheckConstraint("board_version > 0", name="ck_pms_projects_board_version_positive"),
    )
