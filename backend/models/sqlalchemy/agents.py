from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy import SQLAlchemyBase


class Agent(SQLAlchemyBase):
    """Persist project agent configuration and lifecycle state."""

    __tablename__ = "pms_agents"

    project_id: Mapped[UUID] = sa.Column(
        sa.UUID(as_uuid=False),
        sa.ForeignKey("pms_projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[str] = sa.Column(sa.String(16), nullable=False)
    name: Mapped[str] = sa.Column(sa.String(80), nullable=False)
    description: Mapped[str] = sa.Column(sa.String(240), nullable=False, server_default="")
    instructions: Mapped[str] = sa.Column(sa.Text, nullable=False)
    model: Mapped[str] = sa.Column(sa.String(255), nullable=False)
    memory_policy: Mapped[str] = sa.Column(sa.String(16), nullable=False)
    max_steps_per_run: Mapped[int] = sa.Column(sa.Integer, nullable=False)
    approval_mode: Mapped[str] = sa.Column(sa.String(16), nullable=False)
    status: Mapped[str] = sa.Column(sa.String(16), nullable=False, server_default="active")
    system_tool_names: Mapped[list[str]] = sa.Column(
        JSONB,
        nullable=False,
        server_default=sa.text("'[]'::jsonb"),
    )
    created_by: Mapped[UUID] = sa.Column(sa.UUID(as_uuid=False), nullable=False, index=True)
    created_at: Mapped[datetime] = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )
    updated_at: Mapped[datetime] = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )
    version: Mapped[int] = sa.Column(sa.Integer, nullable=False, server_default="1")

    __table_args__ = (
        sa.Index(
            "uq_pms_agents_project_coordinator",
            "project_id",
            unique=True,
            postgresql_where=sa.text("kind = 'coordinator'"),
        ),
        sa.Index(
            "uq_pms_agents_project_live_name",
            "project_id",
            "name",
            unique=True,
            postgresql_where=sa.text("status <> 'archived'"),
        ),
        sa.CheckConstraint(
            "kind IN ('coordinator', 'worker')",
            name="ck_pms_agents_kind",
        ),
        sa.CheckConstraint(
            "memory_policy IN ('project', 'session', 'none')",
            name="ck_pms_agents_memory_policy",
        ),
        sa.CheckConstraint(
            "approval_mode IN ('project', 'always')",
            name="ck_pms_agents_approval_mode",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'disabled', 'archived')",
            name="ck_pms_agents_status",
        ),
        sa.CheckConstraint(
            "max_steps_per_run > 0",
            name="ck_pms_agents_max_steps_positive",
        ),
        sa.CheckConstraint("version > 0", name="ck_pms_agents_version_positive"),
        sa.CheckConstraint(
            "kind <> 'coordinator' OR status = 'active'",
            name="ck_pms_agents_coordinator_active",
        ),
    )
