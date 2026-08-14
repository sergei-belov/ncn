from uuid import UUID

from pydantic import BaseModel


class DeleteResult(BaseModel):
    """Deletion outcome for one requested identifier."""

    id: int | str | UUID
    deleted: bool


class MultiDeleteResponse(BaseModel):
    """Collection of per-record deletion outcomes."""

    records: list[DeleteResult]
