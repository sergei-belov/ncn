import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy.base import SQLAlchemyBase


class User(SQLAlchemyBase):
    """Abstract table shape for application users."""

    __tablename__ = "users"
    __abstract__ = True

    email: Mapped[str] = sa.Column(sa.String, nullable=False, index=True, unique=True)
    name: Mapped[str] = sa.Column(sa.String, nullable=False)
    password: Mapped[str | None] = sa.Column(sa.String, nullable=True)
