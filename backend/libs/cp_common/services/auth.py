import logging
from datetime import (
    datetime,
    timedelta,
)

import bcrypt
import jwt
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request

from libs.cp_common.models.enum import AuthFlow
from libs.cp_common.models.exceptions.http import UnauthorizedUserHTTPException
from libs.cp_common.models.pydantic import (
    JwtPayload,
    OIDCUser,
)


class OAuth2PasswordBearerCustom(OAuth2PasswordBearer):
    """OAuth2 bearer extractor that uses the shared authorization exception."""

    async def __call__(self, request: Request) -> str | None:
        """Extract a bearer token from a request.

        Args:
            request: HTTP request containing authorization headers.

        Returns:
            The bearer token when present and valid for extraction.

        Raises:
            UnauthorizedUserHTTPException: If the base extractor rejects the
                request.
        """
        try:
            return await OAuth2PasswordBearer.__call__(self, request=request)
        except HTTPException:
            raise UnauthorizedUserHTTPException()


class Authorization:
    """Hash credentials and create or decode authentication tokens."""

    _logger: logging.Logger
    _flow: AuthFlow
    _secret_key: str
    _algorythm: str
    _expires_delta: int
    oauth2_schema: OAuth2PasswordBearerCustom

    def __init__(
        self,
        flow: AuthFlow,
        secret_key: str,
        algorythm: str,
        login_url: str,
        expires_delta: int,
    ):
        """Initialize the authentication service.

        Args:
            flow: Authentication boundary used by the service.
            secret_key: Secret used to sign and verify local tokens.
            algorythm: JWT signing algorithm for local tokens.
            login_url: OAuth2 token endpoint advertised by the API.
            expires_delta: Default local access-token lifetime in seconds.
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        self._flow = flow
        self._secret_key = secret_key
        self._algorythm = algorythm
        self._expires_delta = expires_delta
        self.oauth2_schema = OAuth2PasswordBearerCustom(tokenUrl=login_url)

    def get_password_hash(self, password: str) -> str:
        """Get hash of the provided password.

        Args:
            password (str): password

        Returns:
            str: password hash
        """
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against given hashed password.

        Args:
            plain_password (str): unhashed password
            hashed_password (str): hashed password

        Returns:
            bool: True if passwords are verified, else False
        """
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

    def create_access_token(
        self,
        email: str,
        expires_delta: int | None = None,
        subject: str | None = None,
    ) -> str:
        """Create JWT access token.

        Args:
            email (str): user email
            expires_delta (int, optional): JWT token expiration time in seconds.
                If not provided - defaults to ACCESS_TOKEN_EXPIRE.
            subject (str, optional): stable persisted user identifier.

        Returns:
            str: JWT access token
        """
        expires_delta = expires_delta or self._expires_delta
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        jwt_payload = JwtPayload(email=email, sub=subject, exp=expire)
        encoded_jwt = jwt.encode(
            payload=jwt_payload.model_dump(exclude_none=True),
            key=self._secret_key,
            algorithm=self._algorythm,
        )
        return encoded_jwt

    def decode_token_payload(self, token: str) -> dict:
        """Decode a token accepted by the configured authentication boundary.

        Local tokens are verified by this service. OIDC tokens are verified by
        the mandatory API gateway before they can reach this application, so the
        backend only reads their claims for domain-level authorization.
        """
        if self._flow == AuthFlow.LOCAL:
            return jwt.decode(
                jwt=token,
                key=self._secret_key,
                algorithms=[self._algorythm],
            )
        return jwt.decode(jwt=token, options={"verify_signature": False})

    def decode_access_token(self, token: str) -> JwtPayload:
        """Decode JWT access token and get JWT payload.

        Args:
            token (str): JWT access token

        Returns:
            JwtPayload: JWT payload with user ID and expiration time
        """
        decoded_payload = self.decode_token_payload(token)
        if self._flow == AuthFlow.LOCAL:
            payload = decoded_payload
        else:
            oidc_user = OIDCUser.model_validate(decoded_payload)
            payload = JwtPayload(email=oidc_user.email, sub=oidc_user.sub)
        return JwtPayload.model_validate(payload)
