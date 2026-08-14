from __future__ import annotations

from abc import abstractmethod
from typing import Protocol

from sqlalchemy.ext.asyncio import session


class Database(Protocol):
    """Protocol for a database that creates sessions and connects."""

    @abstractmethod
    def session(self) -> SessionHandler:
        """Create a context manager for a database session."""

    @abstractmethod
    async def connect(self) -> None:
        """Initialize the database connection resources."""


class SessionHandler(Protocol):
    """Protocol for transactional asynchronous session context managers."""

    @abstractmethod
    async def __aenter__(self) -> session.AsyncSession:
        """Begin a transaction and return its asynchronous session."""

    async def __aexit__(self, exception_type: type, exception: Exception, _traceback) -> None:
        """Commit a successful transaction or roll back a failed one."""
