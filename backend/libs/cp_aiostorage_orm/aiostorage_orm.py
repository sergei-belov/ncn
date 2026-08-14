from abc import (
    ABCMeta,
    abstractmethod,
)
from typing import (
    Any,
    Union,
)

from .operation_result import OperationResult


class AIOStorageORM(metaclass=ABCMeta):
    """Abstract lifecycle and bulk-operation interface for async storage."""

    _db_instance: Any

    @abstractmethod
    def __init__(
        self,
        client: Any = None,
        host: Union[str, None] = None,
        port: int = 6379,
        db: int = 0,
    ) -> None:
        """Initialize a storage client from a client object or connection data."""

        raise NotImplementedError

    @abstractmethod
    async def init(self) -> None:
        """Initialize the underlying storage connection."""

        raise NotImplementedError

    @abstractmethod
    async def save(self, item) -> OperationResult:
        """Persist one storage item."""

        raise NotImplementedError

    @abstractmethod
    async def bulk_create(self, items: list) -> OperationResult:
        """Persist multiple storage items."""

        raise NotImplementedError

    @abstractmethod
    async def bulk_delete(self, items: list) -> OperationResult:
        """Delete multiple storage items."""

        raise NotImplementedError

    @abstractmethod
    async def delete(self, item) -> OperationResult:
        """Delete one storage item."""

        raise NotImplementedError
