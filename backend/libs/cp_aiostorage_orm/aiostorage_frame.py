from abc import (
    ABCMeta,
    abstractmethod,
)
from typing import Any

from libs.cp_aiostorage_orm.operation_result import OperationResult


class AIOStorageFrame(metaclass=ABCMeta):
    """Abstract interface for ordered collections of storage items."""

    _db_instance: Any

    @abstractmethod
    async def add(self, item_or_items) -> OperationResult:
        """Add one or more items to the frame."""

        raise NotImplementedError

    @abstractmethod
    async def clear(self, item_or_items) -> OperationResult:
        """Remove one or more items from the frame."""

        raise NotImplementedError

    @abstractmethod
    async def get(self, item_or_items) -> list:
        """Retrieve frame values corresponding to one or more items."""

        raise NotImplementedError
