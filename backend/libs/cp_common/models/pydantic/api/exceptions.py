from pydantic import BaseModel


class DetailItem(BaseModel):
    """Structured detail item carried by shared HTTP exceptions."""

    message: str = "Неизвестная ошибка на сервере"
    detail: str = ""
    help: str = ""
    code: str = "???"
