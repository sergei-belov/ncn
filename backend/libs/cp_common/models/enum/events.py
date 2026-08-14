from enum import StrEnum


class EventPriority(StrEnum):
    """Relative delivery priorities for broker events."""

    HIGH: str = "high"
    MEDIUM: str = "medium"
    LOW: str = "low"
