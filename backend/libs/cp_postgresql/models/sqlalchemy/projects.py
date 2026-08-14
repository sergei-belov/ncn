import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy.base import SQLAlchemyBase


class Project(SQLAlchemyBase):
    """Abstract table shape for projects."""

    __tablename__ = "projects"
    __abstract__ = True

    name: Mapped[str] = sa.Column(sa.String, nullable=False)
    description: Mapped[str] = sa.Column(sa.Text, nullable=True)
