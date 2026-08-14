from pydantic import (
    BaseModel,
    model_validator,
)

from libs.cp_common.models.pydantic.api.mixins import (
    OffsetLimitQueriesMixin,
    SearchQueriesMixin,
    SortingQueriesMixin,
)


__all__ = [
    "MetaList",
    "ViewList",
    "ViewListQueries",
]


class MetaList(BaseModel):
    """Offset pagination metadata for list responses."""

    total_count: int
    offset: int | None = None
    limit: int | None = None


class ViewList(BaseModel):
    """Generic list response with offset pagination metadata."""

    data: list[BaseModel]
    meta: MetaList


class ViewListQueries(
    OffsetLimitQueriesMixin,
    SearchQueriesMixin,
    SortingQueriesMixin,
):
    """Combined offset, search, and sorting list queries."""

    @model_validator(mode="before")
    def strip_and_to_lower_all_text_fields(self) -> "ViewListQueries":
        """Strip and lowercase every textual query value."""

        for k, v in self.items():
            if isinstance(v, str):
                self[k] = v.strip().lower()
        return self
