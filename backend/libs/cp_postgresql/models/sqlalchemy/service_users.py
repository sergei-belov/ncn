import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy.base import SQLAlchemyBase


class ServiceUser(SQLAlchemyBase):
    """Abstract table shape for service-specific user access."""

    __tablename__ = "service_users"
    __abstract__ = True

    service: Mapped[str] = sa.Column(sa.String(50), nullable=False)
    project_user_id: Mapped[sa.UUID] = sa.Column(sa.UUID(as_uuid=False), nullable=False)
    role: Mapped[str] = sa.Column(sa.String(20), nullable=False)
