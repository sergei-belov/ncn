import copy
import logging
import pickle
from typing import (
    Any,
    Mapping,
    Type,
    TypeVar,
    Union,
    cast,
)

import redis.asyncio as redis
from pydantic import BaseModel
from redis.asyncio.client import Pipeline

from libs.cp_aiostorage_orm.aiostorage_frame import AIOStorageFrame
from libs.cp_aiostorage_orm.operation_result import (
    OperationResult,
    OperationStatus,
)


# Redis: переопределения типов для корректной работы линтеров
_Value = Union[bytes, float, int, str]
_Key = Union[str, bytes]
ResponseT = Any

T = TypeVar("T", bound="AIORedisFrame")
KEYS_DELIMITER = "."


class AIORedisFrame(AIOStorageFrame):
    """Store a size-bounded frame of serialized objects in a Redis list."""

    _table: str
    _objects: list[BaseModel]
    _params: Mapping[_Key, _Value]
    _db_instance: Union[redis.Redis, None] = None
    _frame_size: int = 1
    _keys_positions: dict

    class Meta:
        """Configure the Redis key template for frame subclasses."""

        table: str = ""  # Pattern имени записи, например, "subsystem.{subsystem_id}.tag.{tag_id}"

    def __init_subclass__(cls) -> None:
        """Derive key-template parameter positions for a frame subclass."""

        cls._keys_positions = {
            index.replace("{", "").replace("}", ""): key
            for key, index in enumerate(cls.Meta.table.split(KEYS_DELIMITER))
            if index.startswith("{") and index.endswith("}")
        }
        for param in cls._keys_positions.keys():
            if param in cls.__annotations__:
                del cls.__annotations__[param]

    def __init__(self, objects: list | None = None, length: int = 1, **kwargs) -> None:
        """Initialize a frame with key parameters and maximum length.

        Args:
            objects: Initial objects held by the frame.
            length: Maximum entries retained in Redis.
            **kwargs: Values used to resolve the configured Redis key template.
        """

        if objects:
            self.objects = objects
        else:
            self.objects = []

        self._object_class = self.__class__.__annotations__["objects"].__args__[0]
        self.length = length

        # Формирование изолированной среды с данными класса для дальнейшей работы с БД
        self._table = self.__class__.Meta.table.format(**kwargs)
        self._params = {key: kwargs.get(key, None) for key in self.__class__.__annotations__}
        # Перегрузка методов для экземпляра класса
        self.using = self.instance_using  # type: ignore

    @classmethod
    def _set_global_instance(cls: Type[T], db_instance: redis.Redis) -> None:
        """Bind the frame class to the default Redis connection."""

        cls._db_instance = db_instance

    @classmethod
    async def add(
        cls,
        item_or_items: Union[T, list[T]],
        expire: int | None = None,
    ) -> OperationResult:
        """Append one or more frames using a Redis pipeline.

        Args:
            item_or_items: Frame or frames whose objects are appended.
            expire: Optional TTL applied to each Redis list.

        Returns:
            Success or failure result for the pipeline operation.
        """
        async with cls._db_instance.pipeline() as pipe:
            try:
                items = cls._get_items(item_or_items)
                _ = [await cls._add_item(item=item, pipe=pipe, expire=expire) for item in items]  # type: ignore
                await pipe.execute()
            except Exception as exception:
                logging.exception(exception)
                return OperationResult(
                    status=OperationStatus.failed,
                    message=str(exception),
                )

        return OperationResult(status=OperationStatus.success)

    @classmethod
    async def clear(cls, item_or_items: Union[T, list[T]]) -> OperationResult:
        """Delete one or more frames from Redis."""

        try:
            items = cls._get_items(item_or_items)

            _ = [await cls._db_instance.delete(item._table) for item in items]

        except Exception as exception:
            logging.exception(exception)
            return OperationResult(
                status=OperationStatus.failed,
                message=str(exception),
            )
        return OperationResult(status=OperationStatus.success)

    @classmethod
    async def get(cls, item_or_items: Union[T, list[T]], expire: int | None = None) -> T | list[T | None] | None:
        """Load and deserialize one or more frames from Redis.

        Args:
            item_or_items: Frame key or keys to retrieve.
            expire: Optional refreshed TTL for retrieved frames.

        Returns:
            One populated frame for scalar input or a list for collection input.
        """
        items = cls._get_items(item_or_items)

        return_items = []

        async with cls._db_instance.pipeline() as pipe:
            _ = [pipe.lrange(item._table, 0, item.length - 1) for item in items]
            return_objects = await pipe.execute()
        if expire:
            async with cls._db_instance.pipeline() as pipe:
                _ = [pipe.expire(item._table, time=expire) for item in items]
                await pipe.execute()
        for item, return_values in zip(items, return_objects):
            if return_values:
                item.objects = [pickle.loads(v) for v in return_values[::-1]]
            return_items.append(item)

        if isinstance(item_or_items, AIORedisFrame):
            return return_items[0]

        return return_items

    def as_dict(self) -> dict[str, Any]:
        """Return key-template values and annotated frame fields as a dictionary."""

        dict_ = {k: self._table.split(KEYS_DELIMITER)[v] for k, v in self._keys_positions.items()}
        for key in self.__annotations__:
            dict_[key] = getattr(self, key)
        return dict_

    def instance_using(self: T, db_instance: Union[redis.Redis, None] = None) -> T:
        """Return a shallow frame copy bound to a specific Redis connection."""

        copied_instance: T = copy.copy(self)
        copied_instance._db_instance = db_instance
        return copied_instance

    @classmethod
    def using(cls: Type[T], db_instance: Union[redis.Redis, None] = None) -> T:
        """Return a frame subclass view bound to a Redis connection."""

        class CopiedClass(cls):  # type: ignore
            """Connection-bound dynamic frame subclass."""

            _db_instance = db_instance

        CopiedClass.__annotations__.update(cls.__annotations__)
        CopiedClass.__name__ = cls.__name__
        return cast(T, CopiedClass)

    @staticmethod
    async def _add_item(item: T, pipe: Pipeline, expire: int | None = None) -> None:
        """Queue serialization, insertion, trimming, and expiry for one frame."""

        # item._table содержит строку с подставленными параметрами текущего объекта
        serialized_objects: list[bytes] = [pickle.dumps(_object) for _object in item.objects]

        await pipe.lpush(item._table, *serialized_objects)
        await pipe.ltrim(item._table, start=0, end=item.length - 1)
        if expire:
            await pipe.expire(item._table, time=expire)

    @staticmethod
    def _get_items(item_or_items: Union[T, list[T]]):
        """Normalize one frame or a frame list to a list."""

        if isinstance(item_or_items, AIORedisFrame):
            return [item_or_items]
        return item_or_items

    def __repr__(self) -> str:
        """Return a developer-facing summary of the frame."""

        return f"{self.__class__.__name__}({self._table=}, " f"{self.length=}), " + f"objects: {len(self.objects)}"
