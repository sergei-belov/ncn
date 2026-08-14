import asyncio
import logging
import pickle
import time
from functools import wraps
from typing import (
    Callable,
    Type,
    TypeVar,
    Union,
)

import redis.asyncio as redis
from pydantic import BaseModel
from redis.asyncio.client import Pipeline
from redis.exceptions import ResponseError

from libs.cp_aiostorage_orm.aiostorage_orm import AIOStorageORM
from libs.cp_aiostorage_orm.models import Offset
from libs.cp_aiostorage_orm.operation_result import (
    OperationResult,
    OperationStatus,
)
from libs.cp_aiostorage_orm.redis_impl.aioredis_frame import AIORedisFrame
from libs.cp_aiostorage_orm.redis_impl.aioredis_hash import AIORedisHash
from libs.cp_aiostorage_orm.redis_impl.aioredis_item import AIORedisItem
from libs.cp_aiostorage_orm.redis_impl.aioredis_item import T as SubclassItemType
from libs.cp_aiostorage_orm.redis_impl.aioredis_stream import AIORedisStream
from libs.cp_common import BaseService


ChildItem = TypeVar("ChildItem", bound=AIORedisItem)


class AIORedisORM(BaseService, AIOStorageORM):
    """Coordinate object-oriented Redis storage and stream listeners."""

    _pipe: Pipeline
    _client: redis.Redis

    def __init__(
        self,
        client: Union[redis.Redis, None] = None,
        host: Union[str, None] = None,
        port: int = 6379,
        db: int = 0,
    ) -> None:
        """Initialize the ORM from a Redis client or connection parameters.

        Args:
            client: Existing asynchronous Redis client.
            host: Redis host used when no client is supplied.
            port: Redis TCP port.
            db: Redis logical database number.

        Raises:
            Exception: If neither a client nor host is supplied.
        """
        super().__init__()
        if client:
            self._client = client
        elif host:
            self._client = redis.Redis(host=host, port=port, db=db)
        else:
            raise Exception("AIOStorageORM-init must contains redis_client or host values...")
        if not AIORedisItem._db_instance:
            AIORedisItem._set_global_instance(db_instance=self._client)
        if not AIORedisHash._db_instance:
            AIORedisHash._set_global_instance(db_instance=self._client)
        if not AIORedisStream._db_instance:
            AIORedisStream._set_global_instance(db_instance=self._client)
        if not AIORedisFrame._db_instance:
            AIORedisFrame._set_global_instance(db_instance=self._client)

        self.streams = []

    async def init(self) -> None:
        """Verify that the configured Redis connection is available."""

        await self._raise_for_connection()

    async def start(self):
        """Verify Redis and schedule registered stream consumers."""

        await self.init()
        if self.streams:
            asyncio.gather(*self.streams)

    async def stop(self):
        """Stop the ORM service, which owns no explicit shutdown action."""

        pass

    async def ping(self) -> bool:
        """Return whether the Redis client responds to ping."""

        return await self._client.ping()

    async def _raise_for_connection(self):
        """Retry Redis connectivity checks with decreasing delays.

        Raises:
            ConnectionError: If every connection attempt fails.
        """
        time_for_retry = [5, 2, 1, 0.5, 0.1]
        while time_for_retry:
            if await AIORedisItem._is_connected(AIORedisItem._db_instance):  # type: ignore
                return
            time.sleep(time_for_retry.pop())
        raise ConnectionError("Redis connection error...")

    async def save(self, item: AIORedisItem) -> OperationResult:
        """Persist one Redis item."""

        return await item.save()

    async def bulk_create(self, items: list[SubclassItemType]) -> OperationResult:
        """Serialize and persist multiple Redis items in one pipeline."""

        try:
            async with self._client.pipeline() as pipe:
                for item in items:
                    value = pickle.dumps(item._params)
                    expiration: Union[int, None] = item._ttl if hasattr(item, "_ttl") else None
                    pipe.set(name=item._table, value=value, ex=expiration)
                await pipe.execute()
            return OperationResult(status=OperationStatus.success)
        except Exception as exception:
            self._on_error_actions(exception=exception)
            return OperationResult(
                status=OperationStatus.failed,
                message=str(exception),
            )

    async def bulk_delete(self, items: list[ChildItem]) -> OperationResult:
        """Delete multiple Redis items in one pipeline."""

        try:
            async with self._client.pipeline() as pipe:
                pipe.delete(*[item._table for item in items])
                await pipe.execute()
            return OperationResult(status=OperationStatus.success)
        except Exception as exception:
            self._on_error_actions(exception=exception)
            return OperationResult(
                status=OperationStatus.failed,
                message=str(exception),
            )

    async def _stream_consumer(
        self,
        stream: str,
        function: Callable,
        model: Type[BaseModel],
        limit: int = 10,
        timeout_ms: int = 100,
        offset: Offset = Offset.LATEST,
        **kwargs,
    ):
        """Continuously read a Redis stream and invoke a typed callback.

        Args:
            stream: Redis stream key.
            function: Callback receiving deserialized objects.
            model: Declared Pydantic object type.
            limit: Maximum entries read per request.
            timeout_ms: Blocking read timeout in milliseconds.
            offset: Initial stream position.
            **kwargs: Reserved listener configuration.
        """
        try:
            stream_info = await self._client.xinfo_stream(stream)
            idx = stream_info[offset.value][0]
        except ResponseError:
            logging.debug(f"No such stream {stream}")
            idx = 0

        while True:
            prepared_objs = []
            try:
                result = await self._client.xread(count=limit, streams={stream: idx}, block=timeout_ms)
                if result:
                    data = result[0][1]
                    idx = data[-1][0]

                    for point in data:
                        prepared_objs.extend(pickle.loads(point[1][b"objects"]))

                    await function(prepared_objs)
            except asyncio.exceptions.CancelledError:
                break
            except Exception as exception:
                self._on_error_actions(exception=exception)
            finally:
                prepared_objs.clear()

    async def delete(self, item: AIORedisItem) -> OperationResult:
        """Delete one Redis item."""

        return await item.delete()

    def _on_error_actions(self, exception: Exception) -> None:
        """Log an exception raised during a Redis storage operation."""

        logging.exception(exception)

    def listen_streams(
        self,
        stream: str,
        limit: int = 10,
        timeout_ms: int = 100,
        offset: Offset = Offset.LATEST,
        **kwargs,
    ) -> Callable:
        """Decorator maker.

        Needed only to receive message processing arguments.

        Args:
            stream: Redis Stream topic name
            limit: buffer size for accumulating messages from Kafka
            timeout_ms: number of seconds to fill the buffer
            offset: start offset for messages

        Returns:
            Decorator object
        """

        def decorator(function: Callable) -> Callable:
            """Register a callback and its inferred stream item model."""

            @wraps(function)
            def wrapper(*args, **kwargs):
                """Forward stream objects to the registered callback."""

                return function(*args, **kwargs)

            model = wrapper.__annotations__["data"].__args__[0]
            assert issubclass(model, BaseModel)

            self.streams.append(
                self._stream_consumer(
                    stream=stream,
                    function=function,
                    model=model,
                    limit=limit,
                    timeout_ms=timeout_ms,
                    offset=offset,
                    **kwargs,
                )
            )
            return function

        return decorator
