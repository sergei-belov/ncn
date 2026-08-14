from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from starlette import status

from libs.cp_common.models.pydantic.api import DetailItem


class BaseHTTPException(HTTPException):
    """Base HTTP exception with a normalized list of detail items."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "Неизвестная ошибка на сервере"
    code: str = "500"

    def __init__(
        self,
        status_code: int | None = None,
        detail: DetailItem | list[DetailItem] | None = None,
    ) -> None:
        """Initialize and encode a shared HTTP exception.

        Args:
            status_code: Optional status overriding the subclass default.
            detail: Optional detail item or list of detail items.
        """
        status_code = status_code or self.status_code
        if detail is None or (isinstance(detail, list) and len(detail) == 0):
            items = [DetailItem(message=self.message, code=self.code)]
        elif isinstance(detail, list):
            items = detail
        else:
            items = [detail]
        detail = []
        for item in items:
            detail.append(
                {
                    "code": item.code,
                    "message": item.message,
                    "detail": item.detail,
                    "help": item.help,
                }
            )
        detail = jsonable_encoder(detail)
        super().__init__(status_code=status_code, detail=detail)


class UnauthorizedUserHTTPException(BaseHTTPException):
    """Report failure to authenticate the current user."""

    status_code: int = status.HTTP_401_UNAUTHORIZED
    message: str = "Не удалось авторизовать пользователя"
    code: str = "401"


class InvalidCredentialsHTTPException(BaseHTTPException):
    """Report invalid login credentials."""

    status_code: int = status.HTTP_401_UNAUTHORIZED
    message: str = "Неверный логин или пароль"
    code: str = "402"


class PermissionDeniedHTTPException(BaseHTTPException):
    """Report insufficient permission for a requested resource."""

    status_code: int = status.HTTP_403_FORBIDDEN
    message: str = "В доступе к запрашиваемому ресурсу отказано"
    code: str = "403"


class RequestedDataNotFoundHTTPException(BaseHTTPException):
    """Report that requested data could not be found."""

    status_code: int = status.HTTP_404_NOT_FOUND
    message: str = "Запрашиваемые данные не найдены"
    code: str = "404"


class ObjectAlreadyExistsHTTPException(BaseHTTPException):
    """Report a conflict with an existing object."""

    status_code: int = status.HTTP_409_CONFLICT
    message: str = "Попытка создать уже существующий объект"
    code: str = "409"


class ContentSizeHTTPException(BaseHTTPException):
    """Report content that exceeds the accepted size."""

    status_code: int = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    message: str = "Размер объекта слишком большой"
    code: str = "413"


class MediaTypeHTTPException(BaseHTTPException):
    """Report an unsupported request media type."""

    status_code: int = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    message: str = "Некорректный тип загружаемых данных"
    code: str = "415"


class UnprocessableEntityHTTPException(BaseHTTPException):
    """Report semantically invalid request data."""

    status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY
    message: str = "Некорректные входящие данные для выполнения запрашиваемого действия"
    code: str = "422"


class InternalServerHTTPException(BaseHTTPException):
    """Report an unexpected internal server failure."""

    pass
