import json
from datetime import datetime
from typing import Annotated
from uuid import UUID

import numpy as np
from pydantic import (
    PlainSerializer,
    WithJsonSchema,
)
from pydantic.functional_validators import BeforeValidator


DT_STRING_FORMAT = "%Y-%m-%d %H:%M:%S"


def convert_to_dt(value: int | str | datetime) -> datetime:
    """Convert a datetime, formatted string, or epoch milliseconds to datetime.

    Args:
        value: Value to normalize.

    Returns:
        The normalized datetime.
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and not value.isdigit():
        return datetime.strptime(value, DT_STRING_FORMAT)
    return datetime.fromtimestamp(int(value) / 1000)


DateTimeSerialized = Annotated[
    datetime,
    PlainSerializer(lambda dt: int(dt.timestamp() * 1000), return_type=int, when_used="json"),
    BeforeValidator(convert_to_dt),
    WithJsonSchema({"type": "integer", "examples": [1711621458000]}),
]
TimestampToDatetime = Annotated[
    datetime,
    BeforeValidator(lambda ts: datetime.fromtimestamp(int(ts) / 1000)),
    WithJsonSchema({"type": "integer", "examples": [1711621458000]}),
]
UUIDSerialized = Annotated[UUID, PlainSerializer(lambda uuid: str(uuid), return_type=str, when_used="always")]
TimestampToFloat = Annotated[
    float,
    BeforeValidator(lambda ts: int(ts) / 1000),
    WithJsonSchema({"type": "integer", "examples": [1711621458000]}),
]

RoundFloat = Annotated[float, PlainSerializer(lambda value: round(value, 3), return_type=float, when_used="json")]
FloatRoundSerialized = Annotated[
    float,
    PlainSerializer(
        lambda value: np.round(value, (-np.round(np.log10(np.abs(value) + 1e-6)).astype(int) + 4)),
        return_type=float,
        when_used="json",
    ),
    WithJsonSchema({"type": "float", "examples": [0.0]}),
]

ArraySerialized = Annotated[
    list,
    BeforeValidator(lambda data: json.loads(data) if type(data) == str else data),
    PlainSerializer(lambda data: json.dumps(data), return_type=str, when_used="always"),
]
DictSerialized = Annotated[
    dict,
    BeforeValidator(lambda data: json.loads(data) if type(data) == str else data),
    PlainSerializer(lambda data: json.dumps(data), return_type=str, when_used="always"),
]
JsonSerialized = Annotated[dict | list, BeforeValidator(lambda data: json.loads(data) if type(data) == str else data)]
