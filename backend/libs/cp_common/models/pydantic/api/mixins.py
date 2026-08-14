from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    PrivateAttr,
    conint,
    model_validator,
)

from libs.cp_common.models.enum import SortOrder


__all__ = [
    "DateTimeToTimestampMixin",
    "TimeAuditMixin",
    "UserAuditMixin",
    "LifecycleMixin",
    "OffsetLimitQueriesMixin",
    "SearchQueriesMixin",
    "SortingQueriesMixin",
    "NoneValidationMixin",
]


class DateTimeToTimestampMixin(BaseModel):
    """Convert datetime input values to millisecond timestamps."""

    @model_validator(mode="before")
    def convert_datetime_to_timestamp_with_microseconds(self) -> "BaseModel":
        """Convert every datetime mapping value to epoch milliseconds."""

        for k, v in self.items():
            if isinstance(v, datetime):
                self[k] = int(v.timestamp() * 1000)
        return self


class TimeAuditMixin(DateTimeToTimestampMixin, BaseModel):
    """Provide optional creation and update timestamps."""

    created_at: int | None = None
    updated_at: int | None = None


class UserAuditMixin(BaseModel):
    """Provide optional creator and updater identifiers."""

    created_by_id: UUID | None = None
    updated_by_id: UUID | None = None


class LifecycleMixin(TimeAuditMixin, UserAuditMixin):
    """Combine timestamp and user audit fields."""

    pass


class OffsetLimitQueriesMixin(BaseModel):
    """Provide bounded offset and limit query fields."""

    offset: conint(ge=0) = 0
    limit: conint(ge=1, le=1000) = 10


class SearchQueriesMixin(BaseModel):
    """Provide a free-text search query field."""

    search: str = ""


class SortingQueriesMixin(BaseModel):
    """Provide optional sort field and direction queries."""

    sort_by: str | None = None
    sort_order: SortOrder = SortOrder.DESC


class NoneValidationMixin(BaseModel):
    """Validate that only allowed nullable fields are set as None."""

    _none_allowed_fields: set[str] = PrivateAttr(default_factory=set)

    @model_validator(mode="after")
    def check_none_forbidden_fields(self) -> "NoneValidationMixin":
        """Reject explicit nulls outside the model's nullable allowlist."""

        none_fields = set(field for field, value in self.model_dump(exclude_unset=True).items() if value is None)
        none_forbidden_fields = none_fields.difference(self._none_allowed_fields)
        if none_forbidden_fields:
            raise ValueError(f"`{none_forbidden_fields}` fields can not be None")
        return self
