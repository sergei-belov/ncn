from __future__ import annotations

import copy
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
from redis.exceptions import ConnectionError

from libs.cp_aiostorage_orm.aiostorage_stream import AIOStorageStream
from libs.cp_aiostorage_orm.operation_result import (
    OperationResult,
    OperationStatus,
)


# Redis: переопределения типов для корректной работы линтеров
_Value = Union[bytes, float, int, str]
_Key = Union[str, bytes]
ResponseT = Any

T = TypeVar("T", bound="AIORedisStream")
IN_SUFFIX = "__in"
KEYS_DELIMITER = "."


class AIORedisStream(AIOStorageStream):
    """Store batches of typed objects as entries in a Redis stream."""

    _table: str
    _objects: list[BaseModel]
    _params: Mapping[_Key, _Value]
    _db_instance: Union[redis.Redis, None] = None
    _max_len: int = 1000
    _approximate: bool = True

    class Meta:
        """Configure stream key template, maximum length, and trimming mode."""

        table: str = ""  # Pattern имени записи, например, "subsystem.{subsystem_id}.tag.{tag_id}"
        max_len: int
        approximate: bool

    def __init_subclass__(cls) -> None:
        """Derive key positions and stream options for a subclass."""

        cls._keys_positions = {
            index.replace("{", "").replace("}", ""): key
            for key, index in enumerate(cls.Meta.table.split(KEYS_DELIMITER))
            if index.startswith("{") and index.endswith("}")
        }
        for param in cls._keys_positions.keys():
            if param in cls.__annotations__:
                del cls.__annotations__[param]
        if hasattr(cls.Meta, "max_len"):
            setattr(cls, "_max_len", cls.Meta.max_len)
        if hasattr(cls.Meta, "approximate"):
            setattr(cls, "_approximate", cls.Meta.approximate)

    def __init__(self, **kwargs) -> None:
        """Initialize stream objects and resolve the configured Redis key."""

        self.objects = kwargs.get("objects")
        if not self.objects:
            self.objects = list()
        self._object_class = self.__class__.__annotations__["objects"].__args__[0]
        # Формирование изолированной среды с данными класса для дальнейшей работы с БД
        self._table = self.__class__.Meta.table.format(**kwargs)
        self._params = {key: kwargs.get(key, None) for key in self.__class__.__annotations__}
        # Перегрузка методов для экземпляра класса
        self.using = self.instance_using  # type: ignore

    def __getattr__(self, attr_name: str):
        """Delegate unresolved attributes to the base object implementation."""

        return object.__getattribute__(self, attr_name)

    @classmethod
    def _set_global_instance(cls: Type[T], db_instance: redis.Redis) -> None:
        """Bind the stream class to the default Redis connection."""

        cls._db_instance = db_instance

    @staticmethod
    async def _is_connected(db_instance: redis.Redis) -> bool:
        """Return whether a Redis connection responds to ping."""

        try:
            await db_instance.ping()  # type: ignore
        except ConnectionError:
            return False

        return True

    async def add(self):
        """Append the current object batch to the Redis stream."""

        if not self._db_instance or not await self._is_connected(db_instance=self._db_instance):
            raise Exception("Redis database not connected...")

        await self._db_instance.xadd(
            self._table,
            {"objects": pickle.dumps(self.objects)},
            maxlen=self._max_len,
            approximate=self._approximate,
        )
        return self

    async def get(self, limit: int = 10) -> Union[T, None]:
        """Load objects from the latest bounded stream entries."""

        if not self._db_instance or not await self._is_connected(db_instance=self._db_instance):
            raise Exception("Redis database not connected...")

        self.objects.clear()

        data = await self._db_instance.xrevrange(name=self._table, count=limit)

        for point in data:
            self.objects.extend(pickle.loads(point[1][b"objects"]))

        return self

    def __repr__(self) -> str:
        """Return a developer-facing stream representation."""

        return f"{self.__class__.__name__}({self._table=}, " f"{self.objects=})"

    def instance_using(self: T, db_instance: Union[redis.Redis, None] = None) -> T:
        """Return a shallow stream copy bound to a Redis connection."""

        copied_instance: T = copy.copy(self)
        copied_instance._db_instance = db_instance
        return copied_instance

    @classmethod
    def using(cls: Type[T], db_instance: Union[redis.Redis, None] = None) -> T:
        """Return a stream subclass view bound to a Redis connection."""

        class CopiedClass(cls):  # type: ignore
            """Connection-bound dynamic stream subclass."""

            _db_instance = db_instance

        CopiedClass.__annotations__.update(cls.__annotations__)
        CopiedClass.__name__ = cls.__name__
        return cast(T, CopiedClass)

    async def delete(self) -> OperationResult:
        """Delete this stream from Redis."""

        try:
            if not self._db_instance or not await self._is_connected(db_instance=self._db_instance):
                raise Exception("Redis database not connected...")
            await self._db_instance.delete(self._table)
            return OperationResult(status=OperationStatus.success)
        except Exception as exception:
            return OperationResult(
                status=OperationStatus.failed,
                message=str(exception),
            )
