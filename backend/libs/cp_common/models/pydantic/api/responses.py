from pydantic import (
    BaseModel,
    Field,
)


class DetailItemResponse(BaseModel):
    """Public representation of one shared HTTP exception detail."""

    code: str = Field(default="001")
    message: str = Field(default="Что пошло не так")
    detail: str = Field(default="Где именно что-то пошло не так")
    help: str = Field(default="Возможная подсказка")


class HTTPExceptionResponse(BaseModel):
    """Public response model for shared HTTP exceptions."""

    detail: list[DetailItemResponse]
