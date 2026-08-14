from fastapi import (
    Request,
    status,
)
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from libs.cp_common.models.exceptions.http import UnprocessableEntityHTTPException
from libs.cp_common.models.pydantic.api import DetailItem


FASTAPI_422_EXC_TYPE_TO_RU_PLACEHOLDER_HM = {
    "missing": {
        "message": "Недостаточно данных для выполнения действия",
        "code": "423",
        "detail": "Ожидается '%(field)s' в составе запроса",
    },
    "string_too_short": {
        "message": "Строка в отправленных данных слишком короткая",
        "code": "424",
        "detail": "Минимальный размер '%(field)s' строки - %(min_length)s",
    },
    "string_too_long": {
        "message": "Строка в отправленных данных слишком длинная",
        "code": "425",
        "detail": "Максимальный размер '%(field)s' строки - %(max_length)s",
    },
    "greater_than": {
        "message": "Переданное числовое значение должно быть строго больше",
        "code": "426",
        "detail": "Значение '%(field)s' должно быть строго больше - %(gt)s",
    },
    "greater_than_equal": {
        "message": "Переданное числовое значение должно быть больше либо равно",
        "code": "427",
        "detail": "Значение '%(field)s' должно быть больше либо равно - %(ge)s",
    },
    "less_than_equal": {
        "message": "Переданное числовое значение должно быть меньше либо равно",
        "code": "428",
        "detail": "Значение '%(field)s' должно быть меньше либо равно - %(le)s",
    },
    "less_than": {
        "message": "Переданное числовое значение должно быть строго меньше",
        "code": "429",
        "detail": "Значение '%(field)s' должно быть строго меньше - %(lt)s",
    },
    "string_type": {
        "message": "Переданное значение должно быть строкой",
        "code": "430",
        "detail": "Значение '%(field)s' должно быть строкой",
    },
    "int_type": {
        "message": "Переданное значение должно быть целочисленным",
        "code": "431",
        "detail": "Значение '%(field)s' должно быть целочисленным",
    },
    "int_parsing": {
        "message": "Переданное значение должно быть целочисленным",
        "code": "431",
        "detail": "Значение '%(field)s' должно быть целочисленным",
    },
    "int_from_float": {
        "message": "Переданное значение должно быть целочисленным",
        "code": "431",
        "detail": "Значение '%(field)s' должно быть целочисленным",
    },
    "float_parsing": {
        "message": "Переданное значение должно быть числом с плавающей точкой",
        "code": "432",
        "detail": "Значение '%(field)s' должно быть числом с плавающей точной",
    },
    "bool_type": {
        "message": "Переданное значение должно быть логического типа",
        "code": "433",
        "detail": "Значение '%(field)s' должно быть логического типа",
    },
    "bool_parsing": {
        "message": "Переданное значение должно быть логического типа",
        "code": "433",
        "detail": "Значение '%(field)s' должно быть логического типа",
    },
    "list_type": {
        "message": "Переданное значение должно быть списком",
        "code": "434",
        "detail": "Переданное значение '%(field)s' должно быть списком",
    },
    "too_short": {
        "message": "В переданном списке/объекте должно быть больше элементов",
        "code": "435",
        "detail": "Минимальная длина списка/объекта '%(field)s' - %(min_length)s",
    },
    "too_long": {
        "message": "В переданном списке/объекте слишком много элементов",
        "code": "436",
        "detail": "Максимальная длина списка/объекта '%(field)s' - %(max_length)s",
    },
    "dict_type": {
        "message": "Переданное значение должно быть объектом (словарем)",
        "code": "437",
        "detail": "Переданное значение '%(field)s' должно быть объектом (словарем)",
    },
    "uuid_type": {
        "message": "Переданное значение должно быть типа UUID",
        "code": "438",
        "detail": "Переданное значение '%(field)s' должно быть типа UUID",
    },
    "uuid_parsing": {
        "message": "Переданное значение должно быть типа UUID",
        "code": "438",
        "detail": "Переданное значение '%(field)s' должно быть типа UUID",
    },
    "json_invalid": {
        "message": "Формат отправленного JSON некорректный",
        "code": "439",
        "detail": "С '%(field)s' позиции отправленный JSON перестает быть корректным",
    },
}


async def fastapi_422_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Translate FastAPI validation errors into localized detail items.

    Args:
        request: Request that failed validation.
        exc: Validation errors reported by FastAPI.

    Returns:
        An HTTP 422 response containing deduplicated structured details.
    """
    exceptions = exc.errors()
    processed = set()
    items = []
    for exception in exceptions:
        type_ = exception.get("type")
        placeholder = FASTAPI_422_EXC_TYPE_TO_RU_PLACEHOLDER_HM.get(type_)
        if placeholder is not None:
            fields = exception.get("loc") or ["???"]
            if f"{type_}.{fields[-1]}" in processed:
                continue
            is_index = isinstance(fields[-1], int) and len(fields) > 1
            field = f"{fields[-2]}.{fields[-1]}" if is_index else fields[-1]
            item = DetailItem(
                message=placeholder["message"],
                detail=placeholder["detail"] % dict(field=field, **exception.get("ctx") or {}),
                code=placeholder["code"],
            )
            processed.add(f"{type_}.{fields[-1]}")
        else:
            item = DetailItem(
                message=UnprocessableEntityHTTPException.message,
                code=UnprocessableEntityHTTPException.code,
            )
        items.append(item)

    content = []
    for item in items:
        content.append(
            {
                "code": item.code,
                "message": item.message,
                "detail": item.detail,
                "help": item.help,
            }
        )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=jsonable_encoder(content),
    )


EXCEPTION_HANDLERS = ((RequestValidationError, fastapi_422_exception_handler),)
