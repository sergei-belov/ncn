from enum import StrEnum


class FilterOperation(StrEnum):
    """Comparison operations supported by repository filters."""

    CONTAINS: str = "contains"
    IS: str = "is"
    ISNOT: str = "isnot"
    GTE: str = "gte"
    LTE: str = "lte"
    BEFORE: str = "before"
    AFTER: str = "after"
