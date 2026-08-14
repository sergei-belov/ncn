from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy import SQLAlchemyBase


class ProjectState(SQLAlchemyBase):
    """Persist an ordered workflow state within a project."""

    __tablename__ = "pms_states"

    project_id: Mapped[UUID] = sa.Column(
        sa.UUID(as_uuid=False),
        sa.ForeignKey("pms_projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = sa.Column(sa.String(50), nullable=False)
    color: Mapped[str] = sa.Column(sa.String(7), nullable=False)
    group: Mapped[str] = sa.Column(sa.String(16), nullable=False)
    position: Mapped[int] = sa.Column(sa.Integer, nullable=False)
    is_default: Mapped[bool] = sa.Column(sa.Boolean, nullable=False, server_default=sa.false())
    version: Mapped[int] = sa.Column(sa.Integer, nullable=False, server_default="1")

    __table_args__ = (
        sa.UniqueConstraint("project_id", "position", name="uq_pms_states_project_position"),
        sa.Index("uq_pms_states_project_name_ci", "project_id", sa.func.lower(name), unique=True),
        sa.Index(
            "uq_pms_states_project_default",
            "project_id",
            unique=True,
            postgresql_where=sa.text("is_default"),
        ),
    )
