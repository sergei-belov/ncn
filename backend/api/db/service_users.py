from uuid import UUID

from api.services import Services
from libs.cp_postgresql import BaseDatabaseGeneric
from models import pydantic, sqlalchemy


class ServiceUsersDb(
    BaseDatabaseGeneric[
        sqlalchemy.ServiceUser,
        UUID,
        pydantic.ServiceUserDTO,
        pydantic.ServiceUserCreateDTO,
        pydantic.ServiceUserUpdateFieldsDTO,
    ]
):
    """Project-service authorization restriction repository."""

    database = Services.database
    _table = sqlalchemy.ServiceUser
    _id = UUID
    _model = pydantic.ServiceUserDTO
    _model_create = pydantic.ServiceUserCreateDTO
    _model_update = pydantic.ServiceUserUpdateFieldsDTO
