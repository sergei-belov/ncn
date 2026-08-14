from datetime import date, datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy import SQLAlchemyBase


class WorkItem(SQLAlchemyBase):
    """Persist an ordered work item and its project workflow metadata."""

    __tablename__ = "pms_work_items"

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
    epic_id: Mapped[UUID | None] = sa.Column(
        sa.UUID(as_uuid=False),
        sa.ForeignKey(
            "pms_epics.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_pms_work_items_epic",
        ),
        nullable=True,
        index=True,
    )
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
        sa.UniqueConstraint("project_id", "sequence_id", name="uq_pms_work_items_project_sequence"),
        sa.UniqueConstraint("project_id", "state_id", "rank", name="uq_pms_work_items_state_rank"),
        sa.CheckConstraint(
            "start_date IS NULL OR due_date IS NULL OR start_date <= due_date",
            name="ck_pms_work_items_date_order",
        ),
    )


class WorkItemAssignee(SQLAlchemyBase):
    """Persist a unique user assignment to a work item."""

    __tablename__ = "pms_work_item_assignees"

    work_item_id: Mapped[UUID] = sa.Column(
        sa.UUID(as_uuid=False),
        sa.ForeignKey("pms_work_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = sa.Column(sa.UUID(as_uuid=False), nullable=False, index=True)

    __table_args__ = (
        sa.UniqueConstraint("work_item_id", "user_id", name="uq_pms_work_item_assignees_item_user"),
    )
