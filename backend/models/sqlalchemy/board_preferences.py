from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy import SQLAlchemyBase


class BoardPreference(SQLAlchemyBase):
    """Persist one user's presentation preferences for a project board."""

    __tablename__ = "pms_board_preferences"

    project_id: Mapped[UUID] = sa.Column(
        sa.UUID(as_uuid=False),
        sa.ForeignKey("pms_projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = sa.Column(sa.UUID(as_uuid=False), nullable=False, index=True)
    display: Mapped[dict] = sa.Column(
        JSONB,
        nullable=False,
        server_default=sa.text(
            "'{\"show_priority\":true,\"show_assignees\":true,\"show_due_date\":true,\"show_epic\":true}'::jsonb"
        ),
    )
    collapsed_state_ids: Mapped[list[UUID]] = sa.Column(
        ARRAY(sa.UUID(as_uuid=False)), nullable=False, server_default=sa.text("'{}'")
    )
    version: Mapped[int] = sa.Column(sa.Integer, nullable=False, server_default="1")

    __table_args__ = (
        sa.UniqueConstraint("project_id", "user_id", name="uq_pms_board_preferences_project_user"),
    )
