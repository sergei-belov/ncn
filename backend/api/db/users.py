from uuid import UUID

from api.services import Services
from libs.cp_postgresql import BaseDatabaseGeneric
from models import pydantic, sqlalchemy


class UsersDb(
    BaseDatabaseGeneric[
        sqlalchemy.User,
        UUID,
        pydantic.UserDTO,
        pydantic.UserCreateDTO,
        pydantic.UserUpdateFieldsDTO,
    ]
):
    """Application user repository."""

    database = Services.database
    _table = sqlalchemy.User
    _id = UUID
    _model = pydantic.UserDTO
    _model_create = pydantic.UserCreateDTO
    _model_update = pydantic.UserUpdateFieldsDTO
