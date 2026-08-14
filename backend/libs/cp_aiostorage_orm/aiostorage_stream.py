from abc import (
    ABCMeta,
    abstractmethod,
)
from typing import Any

from libs.cp_aiostorage_orm.operation_result import OperationResult


class AIOStorageStream(metaclass=ABCMeta):
    """Abstract interface for append-only storage streams."""

    _db_instance: Any

    @abstractmethod
    async def add(self) -> OperationResult:
        """Append this item to the stream."""

        raise NotImplementedError

    @abstractmethod
    async def get(self, limit: int):
        """Retrieve up to a bounded number of stream entries."""

        raise NotImplementedError

    @abstractmethod
    async def delete(self) -> OperationResult:
        """Delete this stream item."""

        raise NotImplementedError
