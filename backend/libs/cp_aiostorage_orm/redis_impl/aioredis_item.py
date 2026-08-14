from __future__ import annotations

import copy
import itertools
import pickle
import random
import re
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

from libs.cp_aiostorage_orm.aiostorage_item import AIOStorageItem
from libs.cp_aiostorage_orm.exceptions import (
    MultipleGetParamsException,
    NotEnoughParamsException,
)
from libs.cp_aiostorage_orm.operation_result import (
    OperationResult,
    OperationStatus,
)


# Redis: переопределения типов для корректной работы линтеров
_Value = Union[bytes, float, int, str]
_Key = Union[str, bytes]
ResponseT = Any

T = TypeVar("T", bound="AIORedisItem")
IN_SUFFIX = "__in"
KEYS_DELIMITER = "."
NOISE_PERCENT = 10


class AIORedisItem(AIOStorageItem):
    """Store a typed object as a serialized value under a templated Redis key."""

    _table: str
    _keys_positions: dict[str, int]
    _params: Mapping[_Key, _Value]
    _db_instance: Union[redis.Redis, None] = None
    _ttl: Optional[int] = None

    class Meta:
        """Configure key template, TTL, and TTL randomization for subclasses."""

        table: str = ""  # Pattern имени записи, например, "subsystem.{subsystem_id}.tag.{tag_id}"
        ttl: Optional[int] = None  # Время жизни объекта в базе данных
        floating_ttl: bool = False  # Добавлять ли случайную величину к TTL

    def __init_subclass__(cls) -> None:
        """Derive key positions and TTL settings for an item subclass."""

        cls._keys_positions = {
            index.replace("{", "").replace("}", ""): key
            for key, index in enumerate(cls.Meta.table.split(KEYS_DELIMITER))
            if index.startswith("{") and index.endswith("}")
        }
        for param in cls._keys_positions.keys():
            if param in cls.__annotations__:
                del cls.__annotations__[param]
        # Аргументы, которые используются для дальнейшей проверки и работы
        if hasattr(cls.Meta, "ttl") and cls.Meta.ttl:
            ttl = cls.Meta.ttl
            if hasattr(cls.Meta, "floating_ttl") and cls.Meta.floating_ttl:
                ttl = cls._add_noise_to_ttl(ttl=ttl, noise_percent=NOISE_PERCENT)
            setattr(cls, "_ttl", ttl)

    @staticmethod
    def _add_noise_to_ttl(ttl: int, noise_percent: int) -> int:
        """Add uniformly distributed percentage noise to a TTL.

        Args:
            ttl: Base time to live in seconds.
            noise_percent: Maximum absolute variation as a percentage.

        Returns:
            The randomized time to live.
        """
        noise: int = int(ttl * (2 * random.random() - 1) * (noise_percent / 100))
        ttl += noise
        return ttl

    def set_ttl(self, new_ttl: int) -> None:
        """Override this item's time to live."""

        setattr(self, "_ttl", new_ttl)

    def __init__(self, **kwargs) -> None:
        """Initialize item fields, key parameters, and storage options."""

        for config_key in ("ttl", "frame_size"):
            if config_key in kwargs.keys():
                if config_key == "ttl" and kwargs.get("floating_ttl", False):
                    kwargs[config_key] = self._add_noise_to_ttl(ttl=kwargs[config_key], noise_percent=NOISE_PERCENT)
                setattr(self, f"_{config_key}", kwargs[config_key])
                del kwargs[config_key]
        [self.__dict__.__setitem__(key, value) for key, value in kwargs.items()]  # type: ignore
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
        """Bind the item class to the default Redis connection."""

        cls._db_instance = db_instance

    @staticmethod
    async def _is_connected(db_instance: redis.Redis) -> bool:
        """Return whether a Redis connection responds to ping."""

        try:
            await db_instance.ping()  # type: ignore
        except ConnectionError:
            return False

        return True

    @classmethod
    async def get(cls: Type[T], _item: Union[T, None] = None, expire: int | None = None, **kwargs) -> Union[T, None]:
        """Retrieve one item selected by an instance or exact key parameters.

        Args:
            _item: Optional item whose resolved key is used directly.
            expire: Optional refreshed TTL for the retrieved key.
            **kwargs: Values used to resolve the configured key template.

        Returns:
            The deserialized item when found, otherwise ``None``.

        Raises:
            MultipleGetParamsException: If list-style parameters resolve to
                more than one key.
            NotEnoughParamsException: If the parameters leave a wildcard key.
        """
        if not cls._db_instance or not await cls._is_connected(db_instance=cls._db_instance):
            raise Exception("Redis database not connected...")
        if len(kwargs) and _item:
            raise Exception(f"{cls.__name__}.get() has _item and kwargs. It's not possible.")
        filter: str
        if _item:
            filter = _item._table
        else:
            # Разобрать готовым методом аргуметы в список фильтров
            filters_list: list[str] = cls._get_filters_by_kwargs(**kwargs)
            if len(filters_list) > 1:
                raise MultipleGetParamsException(f"{cls.__name__} invalid (uses __in) params to get method...")
            filter = filters_list[0]
            # Использование маски для выборки одного объекта не предусмотрено
            if not filter or "*" in filter:
                raise NotEnoughParamsException(f"{cls.__name__} not enough params to get method...")
        keys = cls._get_keys_from_mask(filter)
        values: bytes = await cls._db_instance.get(filter)
        if expire:
            await cls._db_instance.expire(filter, time=expire)
        if not values:
            return None
        finded_objects: list[T] = cls._objects_from_db_items([(keys, values)])
        result: Union[T, None] = finded_objects[0]
        return result

    @classmethod
    async def filter(cls: Type[T], _items: Union[list[T], None] = None, expire: int | None = None, **kwargs) -> list[T]:
        """Retrieve items selected by instances or key-pattern parameters.

        Args:
            _items: Optional items whose resolved keys are used directly.
            expire: Optional refreshed TTL for matched keys.
            **kwargs: Exact, wildcard, or ``__in`` key-template parameters.

        Returns:
            Deserialized items for matching Redis keys.
        """
        if not cls._db_instance or not await cls._is_connected(db_instance=cls._db_instance):
            raise Exception("Redis database not connected...")
        if not len(kwargs) and not _items:
            raise Exception(f"{cls.__name__}.filter() has empty filter. OOM possible.")
        if len(kwargs) and _items:
            raise Exception(f"{cls.__name__}.filter() has _items and kwargs. It's not possible.")
        filters_list: list[str]
        keys_list: list[dict]
        values_list: list[bytes]
        if _items:
            filters_list = [item._table for item in _items]
            keys_list = [cls._get_keys_from_mask(item._table) for item in _items]
        else:
            filters_list = list()
            keys_list = list()
            # Формирование списка фильтров для возможности поиска входящих в список
            patterns_list = cls._get_filters_by_kwargs(**kwargs)

            for pattern in patterns_list:
                if "*" in pattern:
                    # Если не передан один из параметров и нужен поиск по ключам
                    item_tables = [table.decode() for table in await cls._db_instance.keys(pattern=pattern)]

                else:
                    # Если все параметры присутствуют, то можно использовать только
                    #   имена атрибутов
                    item_tables = [pattern]
                filters_list.extend(item_tables)
                keys_list.extend([cls._get_keys_from_mask(item_table) for item_table in item_tables])

        async with cls._db_instance.pipeline() as pipe:
            for filter in filters_list:
                pipe.get(filter)
            values_list = await pipe.execute()
        if expire:
            async with cls._db_instance.pipeline() as pipe:
                for filter in filters_list:
                    pipe.expire(filter, time=expire)
                await pipe.execute()

        result: list[T] = cls._objects_from_db_items([(keys, values) for keys, values in zip(keys_list, values_list)])

        return result

    @classmethod
    def _objects_from_db_items(cls: Type[T], items: list[(dict, bytes)]) -> list[T | None]:
        """Deserialize key parameters and values into item instances."""

        # Подготовка базовых данных для формирования объектов из ключей
        #   (уникальные ключи, без имён полей)

        unpacked_items: list[Type[T | None]] = list()
        for item in items:
            params = item[0]
            if item[1]:
                values = pickle.loads(item[1])
                unpacked_items.append(cls(**(params | values)))
            else:
                unpacked_items.append(None)

        return unpacked_items

    @staticmethod
    def _get_list_of_prepared_kwargs(**kwargs: dict) -> list[dict]:
        """Expand ``__in`` parameters into every key-value combination.

        Examples:
            ``{"a__in": [1, 2], "b": 3}`` becomes
            ``[{"a": 1, "b": 3}, {"a": 2, "b": 3}]``.
        """
        basic_kwargs: dict = {}
        extend_kwargs: dict = {}
        # Разделение на словари "с" и "без" списков в значениях
        for key, value in kwargs.items():
            if not key.endswith(IN_SUFFIX):
                basic_kwargs[key] = value
            else:
                extend_kwargs[key.strip(IN_SUFFIX)] = value
        # Формирование итоговых словарей
        result_kwargs: list[dict] = []
        if extend_kwargs:
            # Получить множество комбинаций расширенного словаря
            mixed_kwargs: list[dict] = list(
                dict(zip(extend_kwargs.keys(), values)) for values in itertools.product(*extend_kwargs.values())
            )
            # Обогатить расширенные словари базовым
            result_kwargs = [mixed_item | basic_kwargs for mixed_item in mixed_kwargs]
        else:
            result_kwargs = [basic_kwargs]

        return result_kwargs

    @classmethod
    def _get_filters_by_kwargs(cls: Type[T], **kwargs: dict) -> list[str]:
        """Build Redis key patterns from supplied template parameters."""

        table: str = cls.Meta.table
        # Шаблон для поиска аргументов, которе не были переданы
        patterns: list[str] = re.findall(r"\{[^\}]*\}", table)
        str_filters: list[str] = []
        # Получение сырого списка фильтров
        prepared_kwargs_list: list[dict] = cls._get_list_of_prepared_kwargs(**kwargs)
        # Замена аргументов, которые не переданы, на звездочку
        for prepared_kwargs in prepared_kwargs_list:
            for pattern in patterns:
                clean_key: str = pattern.strip("{").strip("}")
                if clean_key not in prepared_kwargs:
                    table = table.replace(pattern, "*")
            # Заполнение паттерна поиска
            str_filters.append(table.format(**prepared_kwargs))

        return str_filters

    @classmethod
    def _get_keys_from_mask(cls, key: str):
        """Extract named key-template parameters from a resolved Redis key."""

        table: str = cls.Meta.table
        pattern = table.replace("{", "(?P<").replace("}", ">[a-zA-Z\d\-\s\.]+)")  # noqa
        match = re.match(pattern, key)
        return match.groupdict() if match else {}

    @property
    def mapping(self) -> tuple[str, bytes]:
        """Return the resolved Redis key and serialized item parameters."""

        return self._table, pickle.dumps(self._params)

    def __repr__(self) -> str:
        """Return a developer-facing item representation."""

        return f"{self.__class__.__name__}({self._table=}, " f"{self._params=})"

    def __eq__(self, other: Any) -> bool:
        """Compare items by class, key parameters, and resolved table."""

        if isinstance(other, self.__class__):
            return self._params == other._params and self._table == other._table

        return False

    def instance_using(self: T, db_instance: Union[redis.Redis, None] = None) -> T:
        """Return a shallow item copy bound to a Redis connection."""

        copied_instance: T = copy.copy(self)
        copied_instance._db_instance = db_instance
        return copied_instance

    @classmethod
    def using(cls: Type[T], db_instance: Union[redis.Redis, None] = None) -> T:
        """Return an item subclass view bound to a Redis connection."""

        class CopiedClass(cls):  # type: ignore
            """Connection-bound dynamic item subclass."""

            _db_instance = db_instance

        CopiedClass.__annotations__.update(cls.__annotations__)
        CopiedClass.__name__ = cls.__name__
        return cast(T, CopiedClass)

    async def save(self) -> OperationResult:
        """Serialize and persist this item with its optional TTL."""

        try:
            if not self._db_instance or not await self._is_connected(db_instance=self._db_instance):
                raise Exception("Redis database not connected...")
            value = pickle.dumps(self._params)
            expiration: Union[int, None] = self._ttl if hasattr(self, "_ttl") else None
            await self._db_instance.set(name=self._table, value=value, ex=expiration)
            return OperationResult(status=OperationStatus.success)
        except Exception as exception:
            return OperationResult(
                status=OperationStatus.failed,
                message=str(exception),
            )

    async def delete(self) -> OperationResult:
        """Delete this item from Redis."""

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
