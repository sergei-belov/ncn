from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped


__all__ = [
    "TimeAuditMixin",
    "UserAuditMixin",
    "LifecycleMixin",
]


class TimeAuditMixin:
    """Add database-managed creation and update timestamps."""

    created_at: Mapped[datetime] = sa.Column(sa.DateTime, server_default=sa.func.now())
    updated_at: Mapped[datetime] = sa.Column(sa.DateTime, server_default=sa.func.now(), onupdate=datetime.utcnow)


class UserAuditMixin:
    """Add optional creator and updater identifiers."""

    created_by_id: Mapped[sa.UUID | None] = sa.Column(
        sa.UUID(as_uuid=False),
        nullable=True,
    )
    updated_by_id: Mapped[sa.UUID | None] = sa.Column(
        sa.UUID(as_uuid=False),
        nullable=True,
    )


class LifecycleMixin(TimeAuditMixin, UserAuditMixin):
    """Combine time and user audit columns."""

    pass
