from api.db import Database
from api.managers.common import PmsError
from api.services import Services
from api.settings import get_settings
from libs.cp_common.models.enum import AuthFlow
from models import pydantic


class AuthManager:
    """Implement local registration and login workflows."""

    @staticmethod
    def _require_local_auth() -> None:
        """Require the service to use the local authentication flow.

        Raises:
            PmsError: If local authentication routes are disabled.
        """
        if get_settings().AUTH_FLOW != AuthFlow.LOCAL:
            raise PmsError(404, "AUTH_ROUTE_DISABLED", "Local authentication is disabled.")

    @classmethod
    async def register(
        cls,
        user_info: pydantic.PostRegisterRequest,
    ) -> pydantic.PostRegisterResponse:
        """Register a new locally authenticated user.

        Args:
            user_info: Validated registration fields.

        Returns:
            Public data for the newly created user.

        Raises:
            PmsError: If local authentication is disabled or the email already
                belongs to a user.
        """
        cls._require_local_auth()
        async with Services.database.session() as session:
            existing = await Database.users.get(email=user_info.email, session=session)
            if existing:
                raise PmsError(409, "USER_ALREADY_EXISTS", "A user with this email already exists.")
            user = await Database.users.upsert(
                pydantic.UserCreateDTO(
                    email=user_info.email,
                    name=user_info.name,
                    password=Services.auth.get_password_hash(user_info.password),
                ),
                conflict_fields={"email"},
                on_conflict="nothing",
                session=session,
            )
            if user is None:
                raise PmsError(409, "USER_ALREADY_EXISTS", "A user with this email already exists.")
            return pydantic.PostRegisterResponse.model_validate(user)

    @classmethod
    async def login(cls, username: str, password: str) -> pydantic.PostLoginResponse:
        """Authenticate local credentials and issue an access token.

        Args:
            username: User email supplied by the OAuth2 form.
            password: Plaintext password to verify.

        Returns:
            A bearer access token for the authenticated user.

        Raises:
            PmsError: If local authentication is disabled or the credentials
                are invalid.
        """
        cls._require_local_auth()
        email = username.strip().casefold()
        async with Services.database.session() as session:
            user = await Database.users.get(email=email, session=session)
            if (
                not user
                or not user.password
                or not Services.auth.verify_password(password, user.password)
            ):
                raise PmsError(401, "INVALID_CREDENTIALS", "Invalid email or password.")
            return pydantic.PostLoginResponse(
                access_token=Services.auth.create_access_token(
                    email=user.email,
                    subject=str(user.id),
                )
            )
