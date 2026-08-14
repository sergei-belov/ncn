from typing import Optional
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
)


__all__ = ["SQLAlchemyBase"]


class SQLAlchemyBase(DeclarativeBase):
    """Declarative base with UUID identifiers and recursive dictionary export."""

    __abstract__ = True

    id: Mapped[sa.UUID] = sa.Column(sa.UUID(as_uuid=False), primary_key=True, default=uuid4)

    def to_dict(self, obj: Optional["SQLAlchemyBase"] = None):
        """Convert a mapped object and nested mapped values to dictionaries.

        Args:
            obj: Optional mapped object to convert instead of ``self``.

        Returns:
            A dictionary excluding SQLAlchemy's internal instance state.
        """
        dict_ = {}
        exclude_keys = ("_sa_instance_state",)
        for k, v in (obj or self).__dict__.items():
            if k not in exclude_keys:
                if isinstance(v, SQLAlchemyBase):
                    v = self.to_dict(v)
                dict_[k] = v
        return dict_
