from datetime import datetime

from pydantic import BaseModel


__all__ = ["JwtPayload"]


class JwtPayload(BaseModel):
    """Claims used by locally issued and normalized access tokens."""

    email: str
    sub: str | None = None
    exp: datetime | None = None
