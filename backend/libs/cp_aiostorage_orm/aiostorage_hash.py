from abc import (
    ABCMeta,
    abstractmethod,
)
from typing import Any

from libs.cp_aiostorage_orm.operation_result import OperationResult


class AIOStorageHash(metaclass=ABCMeta):
    """Abstract interface for hash-backed storage records."""

    _db_instance: Any

    @abstractmethod
    async def save(self) -> OperationResult:
        """Persist the hash record."""

        raise NotImplementedError

    @abstractmethod
    async def update(self) -> OperationResult:
        """Update the hash record."""

        raise NotImplementedError

    @abstractmethod
    async def get(self):
        """Retrieve the hash record."""

        raise NotImplementedError

    @abstractmethod
    async def delete(self) -> OperationResult:
        """Delete the hash record."""

        raise NotImplementedError
