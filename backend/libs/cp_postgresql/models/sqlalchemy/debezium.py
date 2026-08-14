import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from libs.cp_postgresql.models.sqlalchemy.base import SQLAlchemyBase


class Debezium(SQLAlchemyBase):
    """Abstract heartbeat table shape used by Debezium integrations."""

    __tablename__ = "debezium_heartbeat"
    __abstract__ = True

    id: Mapped[sa.Integer] = sa.Column(sa.Integer(), primary_key=True)
    heartbeat_ts: Mapped[sa.DateTime] = sa.Column(sa.DateTime(), nullable=False)
