from enum import Enum


class Offset(str, Enum):
    """Special Redis stream offsets for the first and latest entries."""

    EARLIEST = "first-entry"
    LATEST = "last-entry"
