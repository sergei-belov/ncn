import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy.base import SQLAlchemyBase


class ProjectUser(SQLAlchemyBase):
    """Abstract table shape for project membership."""

    __tablename__ = "project_users"
    __abstract__ = True

    project_id: Mapped[sa.UUID] = sa.Column(sa.UUID(as_uuid=False), nullable=False)
    user_id: Mapped[sa.UUID] = sa.Column(sa.UUID(as_uuid=False), nullable=False)
    role: Mapped[str] = sa.Column(sa.String(20), nullable=False)
