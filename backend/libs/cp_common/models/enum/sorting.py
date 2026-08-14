from enum import Enum


__all__ = ["SortOrder"]


class SortOrder(str, Enum):
    """Ascending and descending sort directions."""

    ASC = "asc"
    DESC = "desc"
