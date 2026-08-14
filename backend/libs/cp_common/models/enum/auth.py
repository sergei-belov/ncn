from enum import Enum


__all__ = ["AuthFlow"]


class AuthFlow(str, Enum):
    """Supported authentication boundaries for a service."""

    LOCAL = "local"
    KEYCLOAK = "keycloak"
