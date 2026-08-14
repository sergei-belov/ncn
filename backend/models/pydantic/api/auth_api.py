from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from models.pydantic.api.common_api import APIModel


class UserAPI(APIModel):
    """Public representation of an application user."""

    id: UUID
    email: str
    name: str
    created_at: datetime


class PostRegisterRequest(APIModel):
    """Validated payload for local user registration."""

    email: str = Field(min_length=3, max_length=100, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Strip and case-normalize a submitted email address."""

        return value.strip().casefold() if isinstance(value, str) else value

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        """Strip surrounding whitespace from a submitted display name."""

        return value.strip() if isinstance(value, str) else value


class PostRegisterResponse(UserAPI):
    """Public user returned after successful registration."""

    pass


class PostLoginResponse(APIModel):
    """Bearer token returned after successful local login."""

    access_token: str
