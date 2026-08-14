from libs.cp_common.models.pydantic import NoneValidationMixin
from libs.cp_postgresql.models.sqlalchemy.uuid_model import UUIDModel


class ProjectDTO(UUIDModel):
    """Shared representation of a project."""

    name: str
    description: str | None


class ProjectUpdateFieldsDTO(NoneValidationMixin):
    """Optional fields used to update a shared project."""

    name: str | None = None
    description: str | None = None

    _none_allowed_fields = {"description"}
