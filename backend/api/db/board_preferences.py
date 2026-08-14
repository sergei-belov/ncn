from uuid import UUID

from api.services import Services
from libs.cp_postgresql import BaseDatabaseGeneric
from models import pydantic, sqlalchemy


class BoardPreferencesDb(
    BaseDatabaseGeneric[
        sqlalchemy.BoardPreference,
        UUID,
        pydantic.BoardPreferenceDTO,
        pydantic.BoardPreferenceCreateDTO,
        pydantic.BoardPreferenceUpdateFieldsDTO,
    ]
):
    """Provide persistence operations for per-user board preferences."""

    database = Services.database
    _table = sqlalchemy.BoardPreference
    _id = UUID
    _model = pydantic.BoardPreferenceDTO
    _model_create = pydantic.BoardPreferenceCreateDTO
    _model_update = pydantic.BoardPreferenceUpdateFieldsDTO
