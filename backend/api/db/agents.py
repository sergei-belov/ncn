from uuid import UUID

from api.services import Services
from libs.cp_postgresql import BaseDatabaseGeneric
from models import pydantic, sqlalchemy


class AgentsDb(
    BaseDatabaseGeneric[
        sqlalchemy.Agent,
        UUID,
        pydantic.AgentDTO,
        pydantic.AgentCreateDTO,
        pydantic.AgentUpdateFieldsDTO,
    ]
):
    """Provide persistence operations for agent records."""

    database = Services.database
    _table = sqlalchemy.Agent
    _id = UUID
    _model = pydantic.AgentDTO
    _model_create = pydantic.AgentCreateDTO
    _model_update = pydantic.AgentUpdateFieldsDTO
