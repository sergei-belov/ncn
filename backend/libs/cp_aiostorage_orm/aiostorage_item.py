from __future__ import annotations

from abc import (
    ABCMeta,
    abstractmethod,
)
from typing import Union

from libs.cp_aiostorage_orm.operation_result import OperationResult


class AIOStorageItem(metaclass=ABCMeta):
    """Abstract model for one storage object.

    Subclasses define typed fields and a nested ``Meta`` configuration with a
    key template and optional time to live, for example::

        class MyModel(AIOStorageItem):
            date_time: float
            any_value: int

            class Meta:
                table = "subsystem.{subsystem_id}.tag.{tag_id}"
                ttl = 3600
    """

    @classmethod
    @abstractmethod
    async def get(cls, _item, **kwargs) -> Union[AIOStorageItem, None]:
        """Retrieve one object selected by an item or keyword filters."""

        raise NotImplementedError

    @classmethod
    @abstractmethod
    async def filter(cls, _items, **kwargs) -> list:
        """Retrieve objects matching supplied items or keyword filters."""

        raise NotImplementedError

    @classmethod
    @abstractmethod
    def using(cls, db_instance) -> AIOStorageItem:
        """Return a subclass view bound to a specific storage connection."""

        raise NotImplementedError

    @abstractmethod
    async def save(self) -> OperationResult:
        """Persist this item."""

        raise NotImplementedError

    @abstractmethod
    async def delete(self) -> OperationResult:
        """Delete this item."""

        raise NotImplementedError

    @abstractmethod
    def set_ttl(self, new_ttl) -> None:
        """Override this item's time to live."""

        raise NotImplementedError
