from enum import Enum


__all__ = [
    "ProjectRole",
    "ServiceRole",
]


class ProjectRole(str, Enum):
    """Legacy project membership roles used by shared libraries."""

    OWNER = "owner"
    ADMIN = "admin"
    USER = "user"


class ServiceRole(str, Enum):
    """Access modes granted to users of a service."""

    READ = "read"
    WRITE = "write"
    COMMENT = "comment"
