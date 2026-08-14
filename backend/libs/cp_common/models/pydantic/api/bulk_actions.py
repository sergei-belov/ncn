from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
)

from libs.cp_common.models.pydantic.validators import CheckItemIdsAndParameters


class BulkBaseRequest(BaseModel, CheckItemIdsAndParameters):
    """Base payload for bulk actions selected by IDs or parameters."""

    item_ids: list[UUID] | None = Field(default=None, min_length=1)
    parameters: dict | None = None
    data: dict


class BulkBaseResponse(BaseModel):
    """Base response reporting the number of affected bulk items."""

    items_count: int
