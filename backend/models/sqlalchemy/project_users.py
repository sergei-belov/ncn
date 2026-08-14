from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy import SQLAlchemyBase


class ProjectUser(SQLAlchemyBase):
    """A user's role inside a project."""

    __tablename__ = "project_users"

    project_id: Mapped[UUID] = sa.Column(
        sa.UUID(as_uuid=False),
        sa.ForeignKey("pms_projects.id", ondelete="CASCADE", deferrable=True),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = sa.Column(
        sa.UUID(as_uuid=False),
        sa.ForeignKey("users.id", ondelete="CASCADE", deferrable=True),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = sa.Column(sa.String(16), nullable=False)

    __table_args__ = (
        sa.UniqueConstraint("project_id", "user_id", name="uq_project_users_project_user"),
    )
