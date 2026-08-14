import logging
import time
from collections import defaultdict, deque
from collections.abc import Callable
from typing import Annotated, AsyncGenerator
from uuid import UUID

from fastapi import Depends, Path, Request
from jwt import PyJWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from api.db import Database
from api.managers.common import PmsError
from api.services import Services
from api.settings import get_settings
from models import pydantic


LOGGER = logging.getLogger(__name__)
USER_RATE_WINDOWS: dict[UUID, deque[float]] = defaultdict(deque)


def _enforce_user_rate_limit(user_id: UUID) -> None:
    """Record a request and enforce the per-user rolling rate limit.

    Args:
        user_id: User whose request window is updated.

    Raises:
        PmsError: If the configured request limit is already exhausted.
    """
    now = time.monotonic()
    window = USER_RATE_WINDOWS[user_id]
    while window and window[0] <= now - 60:
        window.popleft()
    if len(window) >= get_settings().RATE_LIMIT_PER_MINUTE:
        raise PmsError(429, "RATE_LIMITED", "Rate limit exceeded.")
    window.append(now)


async def dependency_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a request-scoped database session."""

    async with Services.database.session() as session:
        yield session


def get_user_email(
    token: Annotated[str, Depends(Services.auth.oauth2_schema)],
) -> str:
    """Decode a bearer token and return its normalized email address.

    Args:
        token: OAuth2 bearer token supplied by FastAPI.

    Returns:
        The normalized email address encoded in the token.

    Raises:
        PmsError: If the token is absent, invalid, or lacks a valid email.
    """
    try:
        payload = Services.auth.decode_access_token(token=token)
        return payload.email.strip().casefold()
    except (PyJWTError, ValidationError, AttributeError, TypeError, ValueError) as exc:
        raise PmsError(401, "AUTH_REQUIRED", "A valid bearer token is required.") from exc


async def get_user(
    request: Request,
    email: Annotated[str, Depends(get_user_email)],
    session: Annotated[AsyncSession, Depends(dependency_session)],
) -> pydantic.UserDTO:
    """Resolve the authenticated application user for a request.

    Args:
        request: Current HTTP request.
        email: Normalized email extracted from the bearer token.
        session: Request-scoped database session.

    Returns:
        The authenticated user DTO.

    Raises:
        PmsError: If the token subject does not map to an application user or
            the user has exceeded the request rate limit.
    """
    user = await Database.users.get(email=email, session=session)
    if user is None:
        raise PmsError(401, "AUTH_REQUIRED", "The authenticated user does not exist.")
    _enforce_user_rate_limit(user.id)
    LOGGER.info("method=%r path=%r user_id=%r", request.method, request.url.path, str(user.id))
    return user


async def get_user_authorized(
    request: Request,
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    project_id: Annotated[UUID, Path(description="ID of project")],
    email: Annotated[str, Depends(get_user_email)],
    session: Annotated[AsyncSession, Depends(dependency_session)],
) -> pydantic.UserAuthorizedDTO:
    """Resolve a user and require membership in the routed project.

    Args:
        request: Current HTTP request.
        workspace_slug: Workspace from the route.
        project_id: Project from the route.
        email: Normalized email extracted from the bearer token.
        session: Request-scoped database session.

    Returns:
        User data enriched with the validated project authorization relation.

    Raises:
        PmsError: If the user is unknown, lacks project membership, or exceeds
            the request rate limit.
    """
    user = await Database.users.get_extended_by_email(
        email=email,
        project_id=project_id,
        workspace_slug=workspace_slug,
        session=session,
    )
    if user is None:
        raise PmsError(401, "AUTH_REQUIRED", "The authenticated user does not exist.")
    if (
        user.project_user_id is None
        or user.project_id is None
        or user.workspace_slug is None
        or user.project_role is None
    ):
        raise PmsError(403, "FORBIDDEN", "Project access is required.")
    authorized = pydantic.UserAuthorizedDTO.model_validate(user)
    _enforce_user_rate_limit(authorized.id)
    LOGGER.info(
        "method=%r path=%r user_id=%r project_role=%r",
        request.method,
        request.url.path,
        str(authorized.id),
        authorized.project_role.value,
    )
    return authorized


async def get_user_in_project(
    user: Annotated[pydantic.UserAuthorizedDTO, Depends(get_user_authorized)],
) -> pydantic.UserAuthorizedDTO:
    """Expose an already authorized project user as a route dependency.

    Args:
        user: User validated by the authorization dependency.

    Returns:
        The unchanged authorized user.
    """
    return user


async def get_workspace_actor(
    workspace_slug: Annotated[str, Path(min_length=1, max_length=100)],
    user: Annotated[pydantic.UserDTO, Depends(get_user)],
) -> pydantic.ActorDTO:
    """Build a workspace-scoped actor from an authenticated user.

    Args:
        workspace_slug: Workspace from the route.
        user: Authenticated application user.

    Returns:
        Actor context for workspace-level operations.
    """
    return pydantic.ActorDTO(
        id=user.id,
        workspace_slug=workspace_slug,
        display_name=user.name,
    )


async def get_project_actor(
    user: Annotated[pydantic.UserAuthorizedDTO, Depends(get_user_authorized)],
) -> pydantic.ActorDTO:
    """Build a project-scoped actor from an authorized user.

    Args:
        user: User authorized for the routed project.

    Returns:
        Actor context carrying the user's workspace identity.
    """
    return pydantic.ActorDTO(
        id=user.id,
        workspace_slug=user.workspace_slug,
        display_name=user.name,
    )


def reject_unknown_query_params(*allowed: str) -> Callable[[Request], None]:
    """Create a dependency that rejects query parameters outside an allowlist.

    Args:
        *allowed: Query parameter names accepted by the route.

    Returns:
        A request validator suitable for FastAPI dependency injection.
    """
    allowed_names = frozenset(allowed)

    def validate(request: Request) -> None:
        """Validate one request against the captured query allowlist.

        Args:
            request: HTTP request whose query parameters are inspected.

        Raises:
            PmsError: If one or more query parameters are not allowed.
        """
        unknown = sorted(set(request.query_params) - allowed_names)
        if unknown:
            raise PmsError(
                400,
                "MALFORMED_REQUEST",
                f"Unknown query parameter(s): {', '.join(unknown)}.",
            )

    return validate
