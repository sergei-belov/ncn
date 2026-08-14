from datetime import date, datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy import SQLAlchemyBase


class Epic(SQLAlchemyBase):
    """Persist an ordered project epic and its workflow metadata."""

    __tablename__ = "pms_epics"

    project_id: Mapped[UUID] = sa.Column(
        sa.UUID(as_uuid=False),
        sa.ForeignKey("pms_projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sequence_id: Mapped[int] = sa.Column(sa.Integer, nullable=False)
    title: Mapped[str] = sa.Column(sa.String(255), nullable=False)
    description_html: Mapped[str] = sa.Column(sa.Text, nullable=False, server_default="")
    state_id: Mapped[UUID] = sa.Column(
        sa.UUID(as_uuid=False),
        sa.ForeignKey("pms_states.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    priority: Mapped[str] = sa.Column(sa.String(16), nullable=False, server_default="none")
    start_date: Mapped[date | None] = sa.Column(sa.Date, nullable=True)
    due_date: Mapped[date | None] = sa.Column(sa.Date, nullable=True, index=True)
    rank: Mapped[str] = sa.Column(sa.String(32), nullable=False)
    created_by: Mapped[UUID] = sa.Column(sa.UUID(as_uuid=False), nullable=False, index=True)
    created_at: Mapped[datetime] = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )
    version: Mapped[int] = sa.Column(sa.Integer, nullable=False, server_default="1")

    __table_args__ = (
        sa.UniqueConstraint("project_id", "sequence_id", name="uq_pms_epics_project_sequence"),
        sa.UniqueConstraint("project_id", "rank", name="uq_pms_epics_project_rank"),
        sa.CheckConstraint(
            "start_date IS NULL OR due_date IS NULL OR start_date <= due_date",
            name="ck_pms_epics_date_order",
        ),
    )


class EpicAssignee(SQLAlchemyBase):
    """Persist a unique user assignment to an epic."""

    __tablename__ = "pms_epic_assignees"

    epic_id: Mapped[UUID] = sa.Column(
        sa.UUID(as_uuid=False),
        sa.ForeignKey("pms_epics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = sa.Column(sa.UUID(as_uuid=False), nullable=False, index=True)

    __table_args__ = (
        sa.UniqueConstraint("epic_id", "user_id", name="uq_pms_epic_assignees_epic_user"),
    )
