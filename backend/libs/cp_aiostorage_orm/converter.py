from functools import wraps
from typing import (
    Any,
    Sequence,
    Type,
)

from pydantic import (
    BaseModel,
    TypeAdapter,
)

from libs.cp_aiostorage_orm.redis_impl import AIORedisItem


def redis_to_pydantic(func):
    """
    Decorator for converting AIORedisItem model to Pydantic model specified
    in the __annotations__ attribute of the method.
    It checks the return type of the method and converts it to the specified type.
    """

    def _as_dict(item: Type[AIORedisItem] | None) -> dict[str, Any] | None:
        """Converts AioRedisItem to a linear dictionary view. Field names must be the same."""
        if not item:
            return None
        dict_ = {k: item._table.split(".")[v] for k, v in item._keys_positions.items()}
        dict_.update(item._params)
        return dict_

    @wraps(func)
    async def inner(*args, **kwargs) -> list[BaseModel] | BaseModel | None | Sequence[Type[AIORedisItem]]:
        """Execute the wrapped operation and validate annotated Pydantic output."""

        result = await func(*args, **kwargs)
        if not result or "return" not in func.__annotations__:
            return result

        return_class = func.__annotations__["return"]
        is_list = hasattr(return_class, "__origin__") and isinstance([], return_class.__origin__)

        if not isinstance(result, list):
            result = [result]  # Wrap single item in a list

        result = [_as_dict(r) for r in result]
        return TypeAdapter(return_class).validate_python(result if is_list else result[0])

    return inner
