from pydantic import (
    BaseModel,
    Field,
)


__all__ = ["OIDCUser"]


class OIDCUser(BaseModel):
    """Represents a user object of Keycloak, parsed from access token,

    Notes: Check the Keycloak documentation at https://www.keycloak.org/docs-api/15.0/rest-api/index.html for
    details. This is a mere proxy object.
    """

    sub: str
    iat: int
    exp: int
    scope: str | None = None
    email_verified: bool
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    email: str
    preferred_username: str | None = None
    realm_access: dict | None = None
    resource_access: dict | None = None
    extra_fields: dict = Field(default_factory=dict)

    @property
    def realm_roles(self) -> list[str]:
        """Return the user's realm roles.

        Returns:
            Roles from the token's realm access section.

        Raises:
            ValueError: If the realm access section or its roles are missing.
        """
        if not self.realm_access:
            raise ValueError("The 'realm_access' section of the provided access token is missing.")
        try:
            return self.realm_access["roles"]
        except KeyError as e:
            raise ValueError(
                "The 'realm_access' section of the provided access token did not contain any 'roles'."
            ) from e

    def client_roles(self, client: str) -> list[str]:
        """Return the user's roles for a client.

        Args:
            client: Client identifier in the resource access claim.

        Returns:
            Roles from the client's resource access section.

        Raises:
            ValueError: If resource access or the client's roles are missing.
        """
        if not self.resource_access:
            raise ValueError("The 'resource_access' section of the provided access token is missing")
        try:
            return self.resource_access[client]["roles"]
        except KeyError as e:
            raise ValueError(
                f"The 'resource_access' section of the provided access token did not contain '{client}' with 'roles'"
            ) from e

    def __str__(self) -> str:
        """Return the preferred username as the user string."""

        return self.preferred_username
