"""Unit tests for authentication managers and HTTP identity dependencies."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from jwt import InvalidTokenError

from api.db import Database
from api.dependencies.http import http
from api.dependencies.http.http import (
    USER_RATE_WINDOWS,
    _enforce_user_rate_limit,
    get_project_actor,
    get_user,
    get_user_authorized,
    get_user_email,
    get_workspace_actor,
)
from api.managers.auth import AuthManager
from api.managers.common import PmsError
from api.services import Services
from libs.cp_common.models.enum import AuthFlow
from models import enum, pydantic
from tests.unit.factories import (
    MEMBERSHIP_ID,
    PROJECT_ID,
    USER_ID,
    AsyncContext,
    project_dto,
    project_membership,
    user_dto,
)


def _request() -> SimpleNamespace:
    """Build the request attributes consumed by identity dependencies."""

    return SimpleNamespace(method="GET", url=SimpleNamespace(path="/api/v1/projects"))


def _use_session(monkeypatch: pytest.MonkeyPatch, session: object) -> None:
    """Replace the service session factory with a deterministic context."""

    monkeypatch.setattr(Services.database, "session", lambda: AsyncContext(session))


def _enable_local_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    """Configure manager-local settings for local credential tests."""

    monkeypatch.setattr(
        "api.managers.auth.get_settings",
        lambda: SimpleNamespace(AUTH_FLOW=AuthFlow.LOCAL),
    )


def test_token_email_is_decoded_and_normalized(monkeypatch: pytest.MonkeyPatch) -> None:
    """Normalize an email claim supplied by the configured token decoder."""

    decoder = Mock(return_value=SimpleNamespace(email="  User@Example.COM "))
    monkeypatch.setattr(Services.auth, "decode_access_token", decoder)

    assert get_user_email("token") == "user@example.com"
    decoder.assert_called_once_with(token="token")


def test_invalid_token_is_mapped_to_auth_required(monkeypatch: pytest.MonkeyPatch) -> None:
    """Hide decoder details behind the stable authentication error."""

    monkeypatch.setattr(
        Services.auth,
        "decode_access_token",
        Mock(side_effect=InvalidTokenError("invalid")),
    )

    with pytest.raises(PmsError) as error:
        get_user_email("bad-token")

    assert error.value.status_code == 401
    assert error.value.code == "AUTH_REQUIRED"


@pytest.mark.asyncio
async def test_existing_user_is_resolved_without_provisioning(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return an active user without writing when the email already exists."""

    session = object()
    current = user_dto()
    get = AsyncMock(return_value=current)
    upsert = AsyncMock()
    rate_limit = Mock()
    _use_session(monkeypatch, session)
    monkeypatch.setattr(Database.users, "get", get)
    monkeypatch.setattr(Database.users, "upsert", upsert)
    monkeypatch.setattr(http, "_enforce_user_rate_limit", rate_limit)

    result = await get_user(_request(), current.email)

    assert result == current
    get.assert_awaited_once_with(email=current.email, session=session)
    upsert.assert_not_awaited()
    rate_limit.assert_called_once_with(current.id)


@pytest.mark.asyncio
async def test_missing_user_is_created_from_authenticated_email(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provision an application user whose initial name is the identity email."""

    session = object()
    created = user_dto(email="new@example.com", name="new@example.com")
    get = AsyncMock(return_value=None)
    upsert = AsyncMock(return_value=created)
    _use_session(monkeypatch, session)
    monkeypatch.setattr(Database.users, "get", get)
    monkeypatch.setattr(Database.users, "upsert", upsert)
    monkeypatch.setattr(http, "_enforce_user_rate_limit", Mock())

    result = await get_user(_request(), "new@example.com")

    assert result == created
    create_data = upsert.await_args.kwargs["data"]
    assert create_data.email == "new@example.com"
    assert create_data.name == "new@example.com"
    assert create_data.password_hash is None


@pytest.mark.asyncio
async def test_concurrent_user_provisioning_reloads_winner(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reload a user when a concurrent request wins the email upsert."""

    session = object()
    winner = user_dto(email="race@example.com")
    get = AsyncMock(side_effect=[None, winner])
    _use_session(monkeypatch, session)
    monkeypatch.setattr(Database.users, "get", get)
    monkeypatch.setattr(Database.users, "upsert", AsyncMock(return_value=None))
    monkeypatch.setattr(http, "_enforce_user_rate_limit", Mock())

    result = await get_user(_request(), "race@example.com")

    assert result == winner
    assert get.await_count == 2


@pytest.mark.asyncio
async def test_disabled_user_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reject a persisted user disabled by application policy."""

    _use_session(monkeypatch, object())
    monkeypatch.setattr(Database.users, "get", AsyncMock(return_value=user_dto(is_active=False)))

    with pytest.raises(PmsError) as error:
        await get_user(_request(), "user@example.com")

    assert error.value.status_code == 403
    assert error.value.code == "USER_DISABLED"


def test_per_user_rate_limit_uses_a_rolling_window(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reject requests after the configured per-user minute quota is consumed."""

    USER_RATE_WINDOWS.pop(USER_ID, None)
    monkeypatch.setattr(http.time, "monotonic", Mock(return_value=100.0))
    monkeypatch.setattr(
        http,
        "get_settings",
        lambda: SimpleNamespace(RATE_LIMIT_PER_MINUTE=2),
    )

    _enforce_user_rate_limit(USER_ID)
    _enforce_user_rate_limit(USER_ID)
    with pytest.raises(PmsError) as error:
        _enforce_user_rate_limit(USER_ID)

    assert error.value.status_code == 429
    USER_RATE_WINDOWS.pop(USER_ID, None)


@pytest.mark.asyncio
async def test_project_authorization_builds_enriched_user(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return project relation data only after project and membership checks."""

    session = object()
    current = user_dto()
    membership = project_membership()
    monkeypatch.setattr(Database.projects, "get", AsyncMock(return_value=project_dto()))
    monkeypatch.setattr(Database.project_users, "get", AsyncMock(return_value=membership))

    result = await get_user_authorized(
        _request(),
        "workspace",
        PROJECT_ID,
        current,
        session,
    )

    assert result.id == USER_ID
    assert result.project_user_id == MEMBERSHIP_ID
    assert result.project_role == enum.ProjectRole.ADMIN


@pytest.mark.asyncio
@pytest.mark.parametrize("missing", ["project", "membership"])
async def test_project_authorization_hides_missing_access(
    monkeypatch: pytest.MonkeyPatch,
    missing: str,
) -> None:
    """Return the same forbidden error for absent projects and memberships."""

    project = None if missing == "project" else project_dto()
    membership = None if missing == "membership" else project_membership()
    monkeypatch.setattr(Database.projects, "get", AsyncMock(return_value=project))
    monkeypatch.setattr(Database.project_users, "get", AsyncMock(return_value=membership))

    with pytest.raises(PmsError) as error:
        await get_user_authorized(
            _request(),
            "workspace",
            PROJECT_ID,
            user_dto(),
            object(),
        )

    assert error.value.status_code == 403
    assert error.value.code == "FORBIDDEN"


@pytest.mark.asyncio
async def test_actor_dependencies_preserve_scope_and_identity() -> None:
    """Build workspace and project actor contexts from persisted users."""

    user = user_dto()
    authorized = pydantic.UserAuthorizedDTO(
        **user.model_dump(),
        project_user_id=MEMBERSHIP_ID,
        project_id=PROJECT_ID,
        workspace_slug="workspace",
        project_role=enum.ProjectRole.MEMBER,
    )

    workspace_actor = await get_workspace_actor("workspace", user)
    project_actor = await get_project_actor(authorized)

    assert workspace_actor.id == USER_ID
    assert workspace_actor.workspace_slug == "workspace"
    assert project_actor.id == USER_ID
    assert project_actor.workspace_slug == "workspace"


def test_local_auth_routes_are_disabled_for_external_flow(monkeypatch: pytest.MonkeyPatch) -> None:
    """Hide local registration and login when an external auth flow is configured."""

    monkeypatch.setattr(
        "api.managers.auth.get_settings",
        lambda: SimpleNamespace(AUTH_FLOW=AuthFlow.KEYCLOAK),
    )

    with pytest.raises(PmsError) as error:
        AuthManager._require_local_auth()

    assert error.value.status_code == 404
    assert error.value.code == "AUTH_ROUTE_DISABLED"


@pytest.mark.asyncio
async def test_local_registration_hashes_password_and_returns_public_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Create a unique local user with a password hash and no secret response field."""

    session = object()
    created = user_dto(email="new@example.com", name="New User", password_hash="hash")
    _enable_local_auth(monkeypatch)
    _use_session(monkeypatch, session)
    monkeypatch.setattr(Database.users, "get", AsyncMock(return_value=None))
    upsert = AsyncMock(return_value=created)
    monkeypatch.setattr(Database.users, "upsert", upsert)
    monkeypatch.setattr(Services.auth, "get_password_hash", Mock(return_value="hash"))
    data = pydantic.PostRegisterRequest(
        email=" New@Example.COM ",
        name=" New User ",
        password="long-password",
    )

    result = await AuthManager.register(data)

    assert result.email == "new@example.com"
    assert result.name == "New User"
    assert "password_hash" not in result.model_dump()
    assert upsert.await_args.args[0].password_hash == "hash"


@pytest.mark.asyncio
async def test_duplicate_local_registration_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reject registration when the normalized email already exists."""

    _enable_local_auth(monkeypatch)
    _use_session(monkeypatch, object())
    monkeypatch.setattr(Database.users, "get", AsyncMock(return_value=user_dto()))
    data = pydantic.PostRegisterRequest(
        email="user@example.com",
        name="User",
        password="long-password",
    )

    with pytest.raises(PmsError) as error:
        await AuthManager.register(data)

    assert error.value.status_code == 409
    assert error.value.code == "USER_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_local_login_normalizes_email_and_issues_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify local credentials and create a bearer token for an active user."""

    session = object()
    current = user_dto(password_hash="hash")
    _enable_local_auth(monkeypatch)
    _use_session(monkeypatch, session)
    get = AsyncMock(return_value=current)
    monkeypatch.setattr(Database.users, "get", get)
    monkeypatch.setattr(Services.auth, "verify_password", Mock(return_value=True))
    create_token = Mock(return_value="access-token")
    monkeypatch.setattr(Services.auth, "create_access_token", create_token)

    result = await AuthManager.login(" User@Example.COM ", "password")

    assert result.access_token == "access-token"
    get.assert_awaited_once_with(email="user@example.com", session=session)
    create_token.assert_called_once_with(email=current.email, subject=str(current.id))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "current",
    [None, user_dto(is_active=False), user_dto(password_hash=None)],
)
async def test_invalid_local_login_state_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    current: pydantic.UserDTO | None,
) -> None:
    """Reject unknown, disabled, and passwordless local users uniformly."""

    _enable_local_auth(monkeypatch)
    _use_session(monkeypatch, object())
    monkeypatch.setattr(Database.users, "get", AsyncMock(return_value=current))

    with pytest.raises(PmsError) as error:
        await AuthManager.login("user@example.com", "password")

    assert error.value.status_code == 401
    assert error.value.code == "INVALID_CREDENTIALS"
