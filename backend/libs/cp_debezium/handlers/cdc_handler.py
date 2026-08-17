import inspect
import traceback
from datetime import timedelta
from functools import wraps
from logging import (
    Logger,
    getLogger,
)
from typing import (
    Any,
    Callable,
    Type,
    get_args,
    get_origin,
)

import sqlalchemy as sa
from cp_kafka import KafkaBroker
from cp_postgresql import PostgreSQL
from cp_postgresql.models.exceptions import ObjectAlreadyExistsException
from cp_postgresql.models.sqlalchemy import (
    SQLAlchemyBase,
    UUIDModel,
)
from pydantic import (
    BaseModel,
    ValidationError,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert
from tenacity import (
    RetryError,
    retry,
    stop_after_attempt,
    wait_chain,
    wait_fixed,
)

from libs.cp_debezium.models import (
    enum,
    exceptions,
    pydantic,
)


class DebeziumCDCHandler:
    _logger: Logger = getLogger(__name__)
    _database: PostgreSQL | None = None

    @classmethod
    async def on_create(
        cls,
        obj_model: Type[UUIDModel] | list[Type[UUIDModel]],
        sql_model: Type[SQLAlchemyBase] | None = None,
        exclude_fields: set[str] | None = None,
    ) -> None:
        if not sql_model:
            raise Exception("You need to specify HandlerCDC.on_create(...) for yourself")

        obj_model = obj_model if isinstance(obj_model, list) else [obj_model]
        obj_model = [i.model_dump(mode="json") for i in obj_model]
        if not obj_model:
            return None

        async with cls._database.session() as session:
            insert_statement = pg_insert(sql_model)

            if not exclude_fields:
                update_fields = insert_statement.excluded
            else:
                exclude_fields = exclude_fields | {"id"}
                update_fields = {
                    column.name: getattr(insert_statement.excluded, column.name)
                    for column in sql_model.__table__.columns
                    if column.name not in exclude_fields and not column.primary_key
                }

            insert_statement = insert_statement.on_conflict_do_update(
                index_elements=["id"],
                set_=update_fields,  # type: ignore
            )
            await session.execute(insert_statement, obj_model)
        return None

    @classmethod
    async def on_update(
        cls,
        obj_model: Type[UUIDModel] | list[Type[UUIDModel]],
        sql_model: Type[SQLAlchemyBase] | None = None,
        exclude_fields: set[str] | None = None,
    ) -> None:
        if not sql_model:
            raise Exception("You need to specify HandlerCDC.on_update(...) for yourself")

        obj_model = obj_model if isinstance(obj_model, list) else [obj_model]
        obj_model = [i.model_dump(mode="json") for i in obj_model]
        if not obj_model:
            return None

        async with cls._database.session() as session:
            insert_statement = pg_insert(sql_model)

            if not exclude_fields:
                update_fields = insert_statement.excluded
            else:
                exclude_fields = exclude_fields | {"id"}
                update_fields = {
                    column.name: getattr(insert_statement.excluded, column.name)
                    for column in sql_model.__table__.columns
                    if column.name not in exclude_fields and not column.primary_key
                }

            insert_statement = insert_statement.on_conflict_do_update(
                index_elements=["id"],
                set_=update_fields,  # type: ignore
            )
            await session.execute(insert_statement, obj_model)
        return None

    @classmethod
    async def on_delete(
        cls,
        obj_model: pydantic.DeleteDebeziumCDCModel | list[pydantic.DeleteDebeziumCDCModel],
        sql_model: Type[SQLAlchemyBase] | None = None,
    ) -> None:
        if not sql_model:
            raise Exception("You need to specify HandlerCDC.on_delete(...) for yourself")

        obj_model = obj_model if isinstance(obj_model, list) else [obj_model]
        obj_model = [i.model_dump(mode="json") for i in obj_model]
        if not obj_model:
            return None

        async with cls._database.session() as session:
            await session.execute(sa.delete(sql_model).where(sql_model.id.in_([i["id"] for i in obj_model])))
        return None

    @classmethod
    def sink_objects(
        cls,
        sink_models: list[pydantic.DebeziumSinkCDC],
        broker: KafkaBroker,
        database: PostgreSQL,
    ) -> None:
        cls._database = database
        for m in sink_models:

            async def sinker(
                cdc_models: pydantic.BaseDebeziumCDCModel | list[pydantic.BaseDebeziumCDCModel],
                dto_model: Type[UUIDModel] = m.dto_model,
                sql_model: Type[SQLAlchemyBase] = m.sql_model,
                exclude_fields: set[str] = m.exclude_fields,
            ) -> None:
                await cls.bulk_process(
                    cdc_models=cdc_models, obj_model=dto_model, sql_model=sql_model, exclude_fields=exclude_fields
                )

            broker.listen(topic=m.topic, messages_count=m.batch_size)(sinker)
        return None

    @staticmethod
    def _retry(func: Callable) -> Callable:
        def _is_valid_wait(wait: Any) -> bool:
            return any(isinstance(wait, type) for type in (int, float, timedelta))

        @wraps(func)
        async def inner(*args, **kwargs) -> Any:
            wait = kwargs.pop("wait", None) or 3
            stop = kwargs.pop("stop", None) or 10

            exc = exceptions.DebeziumCDCCallbackHasInvalidRetryOptions(
                "Gotten 'wait' or 'stop' attributes have invalid types. "
                "'wait' - int, float, timedelta, list[int]. "
                "'stop' - int."
            )

            if not isinstance(stop, int):
                raise exc

            if _is_valid_wait(wait=wait):
                wait = wait_fixed(wait=wait)
            elif isinstance(wait, list) and len(wait) > 0 and _is_valid_wait(wait=wait[0]):
                stop = len(wait)
                wait = wait_chain(*[wait_fixed(i) for i in wait])
            else:
                raise exc

            stop += 1
            stop = stop_after_attempt(stop)
            with_retry = retry(wait=wait, stop=stop)(func)
            try:
                return await with_retry(*args, **kwargs)
            except RetryError as ex:
                raise ex.last_attempt.exception()

        return inner

    @classmethod
    @_retry
    async def process(cls, cdc_model: pydantic.BaseDebeziumCDCModel) -> Type[UUIDModel] | None:
        callback = cls._get_callback_by_cdc_operation(cdc_operation=cdc_model.op)
        obj_model_type = cls._get_obj_model_type_from_callback(callback=callback)
        obj = cdc_model.before if cdc_model.op == enum.DebeziumCDCType.DELETE else cdc_model.after
        try:
            return await callback(obj_model=obj_model_type(**obj))
        except ObjectAlreadyExistsException:
            pass
        except Exception as ex:
            cls._logger.error(ex)
            cls._logger.debug(traceback.format_exc())
            raise ex

    @classmethod
    @_retry
    async def bulk_process(  # noqa: C901
        cls,
        cdc_models: list[pydantic.BaseDebeziumCDCModel],
        obj_model: Type[UUIDModel] | None = None,
        sql_model: Type[SQLAlchemyBase] | None = None,
        exclude_fields: set[str] | None = None,
    ) -> list[Type[UUIDModel] | None] | None:
        cdc_models = sorted(cdc_models, key=lambda i: i.source.ts_ms)

        grouped_by_id = {}
        for cdc_model in cdc_models:
            op = enum.DebeziumCDCType.CREATE if cdc_model.op == enum.DebeziumCDCType.READ else cdc_model.op
            obj = cdc_model.before if op == enum.DebeziumCDCType.DELETE else cdc_model.after
            callback = cls._get_callback_by_cdc_operation(cdc_operation=op)
            if not obj_model:
                obj_type = cls._get_obj_model_type_from_callback(callback=callback)
            else:
                obj_type = pydantic.DeleteDebeziumCDCModel if callback == cls.on_delete else obj_model

            try:
                obj = obj_type(**obj)
            except ValidationError as ex:
                cls._logger.error(ex)
                continue

            grouped_by_id.setdefault(str(obj.id), {}).setdefault(op, []).append(obj)

        op_lists = {
            enum.DebeziumCDCType.CREATE: [],
            enum.DebeziumCDCType.UPDATE: [],
            enum.DebeziumCDCType.DELETE: [],
        }
        for id in grouped_by_id:
            for op in op_lists.keys():
                if grouped_by_id[id].get(op):
                    op_lists[op] += grouped_by_id[id][op][-1:]

        try:
            result = []
            if op_lists[enum.DebeziumCDCType.CREATE]:
                result += [await cls.on_create(
                    obj_model=op_lists[enum.DebeziumCDCType.CREATE], sql_model=sql_model, exclude_fields=exclude_fields
                )]
            if op_lists[enum.DebeziumCDCType.UPDATE]:
                result += [await cls.on_update(
                    obj_model=op_lists[enum.DebeziumCDCType.UPDATE], sql_model=sql_model, exclude_fields=exclude_fields
                )]
            if op_lists[enum.DebeziumCDCType.DELETE]:
                result += [await cls.on_delete(
                    obj_model=op_lists[enum.DebeziumCDCType.DELETE], sql_model=sql_model
                )]
            return result
        except ObjectAlreadyExistsException:
            pass
        except Exception as ex:
            cls._logger.error(ex)
            cls._logger.debug(traceback.format_exc())
            raise ex

    @classmethod
    def _get_callback_by_cdc_operation(cls, cdc_operation: enum.DebeziumCDCType) -> Callable:
        hm_cdc_operation_to_callback = {
            enum.DebeziumCDCType.CREATE: cls.on_create,
            enum.DebeziumCDCType.READ: cls.on_create,
            enum.DebeziumCDCType.UPDATE: cls.on_update,
            enum.DebeziumCDCType.DELETE: cls.on_delete,
        }
        callback = hm_cdc_operation_to_callback.get(cdc_operation)
        if callback is None:
            raise exceptions.DebeziumCDCHandlerHasNotSpecifiedCallbackForOperation(
                f"The {cls.__name__} handler has not a specified callback "
                f"method for the '{cdc_operation.value}' operation."
            )
        return callback

    @classmethod
    def _get_obj_model_type_from_callback(cls, callback: Callable) -> Type[BaseModel]:
        callback_signature = inspect.signature(callback)
        obj_model_type = callback_signature.parameters.get("obj_model")
        if obj_model_type is None:
            raise exceptions.DebeziumCDCCallbackHasNotObjModelAttribute(
                f"The {cls.__name__}.{callback.__name__} method has not the required obj_model argument."
            )
        obj_model_type = obj_model_type.annotation
        if get_origin(obj_model_type) is list and (args := get_args(obj_model_type)):
            obj_model_type = args[0]
        if not issubclass(obj_model_type, BaseModel):
            raise exceptions.DebeziumCDCCallbackHasInvalidObjModelAttributeType(
                f"The obj_model argument of {cls.__name__}.{callback.__name__} "
                f"method must be inherited from pydantic.BaseModel."
            )
        return obj_model_type
