from __future__ import annotations

import copy
import pickle
from typing import (
    Any,
    Mapping,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)

import redis.asyncio as redis
from redis.exceptions import ConnectionError

from libs.cp_aiostorage_orm.aiostorage_hash import AIOStorageHash
from libs.cp_aiostorage_orm.operation_result import (
    OperationResult,
    OperationStatus,
)
from libs.cp_aiostorage_orm.redis_impl.aioredis_item import AIORedisItem


# Redis: переопределения типов для корректной работы линтеров
_Value = Union[bytes, float, int, str]
_Key = Union[str, bytes]
ResponseT = Any

T = TypeVar("T", bound="AIORedisItem")
IN_SUFFIX = "__in"
KEYS_DELIMITER = "."


class AIORedisHashItem:
    """Typed key and field values stored inside a Redis hash."""

    def __init__(self, key, *args, **kwargs):
        """Initialize a hash item from its key and annotated values."""

        self.key = key
        self.values = {}
        for attr, _type in self.__annotations__.items():
            self.values[attr] = _type(kwargs[attr])

    def __repr__(self):
        """Return a developer-facing hash item representation."""

        return f"{self.__class__.__name__}(key: {self.key}, values: {self.values})"

    def __getattr__(self, arg):
        """Resolve annotated fields from the stored value mapping."""

        if arg == "key":
            return getattr(self, "key")
        elif arg in self.values:
            return getattr(self, "values")[arg]
        else:
            return getattr(self, arg)


class AIORedisHash(AIOStorageHash):
    """Store typed collections of key-value objects in a Redis hash."""

    _table: str
    _keys_positions: dict[str, int]
    _params: Mapping[_Key, _Value]
    _db_instance: Union[redis.Redis, None] = None
    _ttl: Optional[int] = None
    _key_class: AIOStorageHash
    objects: list[AIOStorageHash]

    class Meta:
        """Configure Redis key template and optional TTL for hash subclasses."""

        table: str = ""  # Pattern имени записи, например, "subsystem.{subsystem_id}.tag.{tag_id}"
        ttl: Optional[int] = None  # Время жизни объекта в базе данных

    def __init_subclass__(cls) -> None:
        """Derive key positions and storage options for a hash subclass."""

        cls._keys_positions = {
            index.replace("{", "").replace("}", ""): key
            for key, index in enumerate(cls.Meta.table.split(KEYS_DELIMITER))
            if index.startswith("{") and index.endswith("}")
        }
        for param in cls._keys_positions.keys():
            if param in cls.__annotations__:
                del cls.__annotations__[param]
        # Аргументы, которые используются для дальнейшей проверки и работы
        if hasattr(cls.Meta, "frame_size"):
            setattr(cls, "_frame_size", cls.Meta.frame_size)
        if hasattr(cls.Meta, "ttl") and cls.Meta.ttl:
            setattr(cls, "_ttl", cls.Meta.ttl)

    def set_ttl(self, new_ttl: int) -> None:
        """Override this hash instance's time to live."""

        setattr(self, "_ttl", new_ttl)

    def __init__(self, **kwargs) -> None:
        """Initialize a hash from key parameters, objects, and storage options."""

        self.objects = kwargs.get("objects")
        self._key_class = self.__class__.__annotations__["objects"].__args__[0]
        # Установка атрибутов из конструктора
        for config_key in ("ttl", "frame_size"):
            if config_key in kwargs.keys():
                setattr(self, f"_{config_key}", kwargs[config_key])
                del kwargs[config_key]
        # Формирование полей модели из переданных дочернему классу аргументов

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
        """Bind the hash class to the default Redis connection."""

        cls._db_instance = db_instance

    @staticmethod
    async def _is_connected(db_instance: redis.Redis) -> bool:
        """Return whether a Redis connection responds to ping."""

        try:
            await db_instance.ping()  # type: ignore
        except ConnectionError:
            return False

        return True

    async def get(self) -> Union[T, None]:
        """Load and deserialize this hash from Redis."""

        if not self._db_instance or not await self._is_connected(db_instance=self._db_instance):
            raise Exception("Redis database not connected...")

        # Разобрать готовым методом аргуметы в список фильтров

        values: dict = await self._db_instance.hgetall(self._table)
        if not values:
            return None
        self.objects = [self._key_class(key=key.decode(), **pickle.loads(value)) for key, value in values.items()]
        return self

    @property
    def mapping(self) -> tuple[str, bytes]:
        """Return the Redis key and serialized hash parameters."""

        return self._table, pickle.dumps(self._params)

    def __repr__(self) -> str:
        """Return a developer-facing hash representation."""

        return f"{self.__class__.__name__}({self._table=}, " f"{self.objects=})"

    def __eq__(self, other: Any) -> bool:
        """Compare hashes by class, key parameters, and resolved table."""

        if isinstance(other, self.__class__):
            return self._params == other._params and self._table == other._table

        return False

    def instance_using(self: T, db_instance: Union[redis.Redis, None] = None) -> T:
        """Return a shallow hash copy bound to a Redis connection."""

        copied_instance: T = copy.copy(self)
        copied_instance._db_instance = db_instance
        return copied_instance

    @classmethod
    def using(cls: Type[T], db_instance: Union[redis.Redis, None] = None) -> T:
        """Return a hash subclass view bound to a Redis connection."""

        class CopiedClass(cls):  # type: ignore
            """Connection-bound dynamic hash subclass."""

            _db_instance = db_instance

        CopiedClass.__annotations__.update(cls.__annotations__)
        CopiedClass.__name__ = cls.__name__
        return cast(T, CopiedClass)

    async def save(self) -> OperationResult:
        """Replace this Redis hash and apply its optional TTL."""

        try:
            if not self._db_instance or not await self._is_connected(db_instance=self._db_instance):
                raise Exception("Redis database not connected...")
            await self._db_instance.delete(self._table)
            expiration: Union[int, None] = self._ttl if hasattr(self, "_ttl") else None
            await self._db_instance.hset(
                name=self._table,
                mapping={obj.key: pickle.dumps(obj.values) for obj in self.objects},
            )
            if expiration:
                print(self._table, expiration)
                await self._db_instance.expire(self._table, time=expiration)
            return OperationResult(status=OperationStatus.success)
        except Exception as exception:
            return OperationResult(
                status=OperationStatus.failed,
                message=str(exception),
            )

    async def update(self) -> OperationResult:
        """Merge this object's values into its Redis hash."""

        try:
            if not self._db_instance or not await self._is_connected(db_instance=self._db_instance):
                raise Exception("Redis database not connected...")

            await self._db_instance.hset(
                name=self._table,
                mapping={obj.key: pickle.dumps(obj.values) for obj in self.objects},
            )
            return OperationResult(status=OperationStatus.success)
        except Exception as exception:
            return OperationResult(
                status=OperationStatus.failed,
                message=str(exception),
            )

    async def delete(self) -> OperationResult:
        """Delete this hash from Redis."""

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
