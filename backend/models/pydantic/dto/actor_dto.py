from uuid import UUID

from pydantic import BaseModel


class ActorDTO(BaseModel):
    """Request actor identity scoped to a workspace."""

    id: UUID
    workspace_slug: str
    display_name: str
    avatar_url: str | None = None
