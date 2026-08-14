from typing import Annotated

from fastapi import Depends, HTTPException, Request
from jwt import PyJWTError

from api.services import Services
from libs.cp_common.models.exceptions.http import UnauthorizedUserHTTPException


async def get_token(request: Request) -> str:
    """Extract a bearer token or raise the shared authorization error.

    Args:
        request: HTTP request containing authorization headers.

    Returns:
        The extracted bearer token.

    Raises:
        UnauthorizedUserHTTPException: If OAuth2 token extraction fails.
    """
    try:
        return await Services.auth.oauth2_schema(request=request)
    except HTTPException:
        raise UnauthorizedUserHTTPException()


def get_user_email(token: Annotated[str, Depends(Services.auth.oauth2_schema)]) -> str:
    """Decode a bearer token and return the contained user email.

    Args:
        token: OAuth2 bearer token.

    Returns:
        Email from the decoded JWT payload.

    Raises:
        UnauthorizedUserHTTPException: If JWT decoding fails.
    """
    try:
        jwt_payload = Services.auth.decode_access_token(token=token)
    except PyJWTError:
        raise UnauthorizedUserHTTPException()
    return jwt_payload.email
