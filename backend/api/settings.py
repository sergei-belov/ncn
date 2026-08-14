from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from libs.cp_common.models.enum import AuthFlow


__all__ = ["ConstSettings", "get_settings"]


class _Settings(BaseSettings):
    """Runtime configuration loaded from environment-compatible settings."""

    APP_ROOT_PATH: str = Field(default="", description="ASGI deployment root path")
    CORS_ALLOW_ORIGINS: list[str] = Field(default_factory=list)
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1)

    AUTH_FLOW: AuthFlow = AuthFlow.KEYCLOAK
    AUTH_SECRET_KEY: str = ""
    AUTH_ALGORITHM: str = Field(default="HS256", min_length=1)
    AUTH_LOGIN_URL: str = Field(default="/api/v1/auth/jwt/login", min_length=1)
    AUTH_ACCESS_TOKEN_EXPIRE_SECONDS: int = Field(default=3600, ge=1)

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USERNAME: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_DATABASE: str = "ncn_pms"
    DB_ECHO_POOL: Literal["debug"] | bool = False
    DB_POOL_SIZE: int = Field(default=10, ge=1)
    DB_CONNECTION_RETRY_PERIOD_SEC: float = Field(default=5.0, ge=0)
    DB_STATEMENT_TIMEOUT_SEC: int = Field(default=5, ge=1)

    model_config = SettingsConfigDict(extra="ignore")


class ConstSettings:
    """Expose immutable service metadata and logging defaults."""

    SERVICE = "ncn-pms"
    TITLE = "NCN Project Management Service"
    DESCRIPTION = "Projects, Kanban states, work items, epics, and board preferences."
    LOG_FORMAT = "%(asctime)s [%(name)s:%(lineno)s] [%(levelname)s]: %(message)s"


@lru_cache
def get_settings(env_file: str | None = None) -> _Settings:
    """Return the cached runtime settings instance.

    Args:
        env_file: Optional dotenv file used when constructing the first instance.

    Returns:
        Cached service settings.
    """
    return _Settings(_env_file=env_file)
