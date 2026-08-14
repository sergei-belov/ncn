"""Unit tests for persisted authorization policy and mutation invariants."""

from unittest.mock import AsyncMock, Mock

import pytest

from api.db import Database
from api.managers.authorization import AuthorizationManager, POLICY_RULES, POLICY_VERSION
from api.managers.common import PmsError
from api.services import Services
from models import enum, pydantic
from tests.unit.factories import (
    OTHER_USER_ID,
    PROJECT_ID,
    USER_ID,
    AsyncContext,
    project_dto,
    project_membership,
    service_restriction,
    user_dto,
    workspace_membership,
)


def _use_session(monkeypatch: pytest.MonkeyPatch, session: object) -> None:
    """Replace the database session factory for one isolated policy test."""

    monkeypatch.setattr(Services.database, "session", lambda: AsyncContext(session))


def _workspace_check(**overrides: object) -> pydantic.AuthorizationCheckRequest:
    """Build a valid workspace authorization decision request."""

    values = {
        "user_id": USER_ID,
        "action": "workspace.member.read",
        "workspace_id": "workspace",
        "resource": {"type": "workspace", "id": "workspace"},
    }
    values.update(overrides)
    return pydantic.AuthorizationCheckRequest(**values)


def _project_check(action: str = "project.read", **overrides: object) -> pydantic.AuthorizationCheckRequest:
    """Build a valid project or service authorization decision request."""

    values = {
        "user_id": USER_ID,
        "action": action,
        "workspace_id": "workspace",
        "project_id": PROJECT_ID,
        "resource": {"type": "project", "id": str(PROJECT_ID)},
    }
    values.update(overrides)
    return pydantic.AuthorizationCheckRequest(**values)


@pytest.mark.asyncio
async def test_workspace_decision_denies_missing_membership(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return an expected denial when no workspace membership exists."""

    monkeypatch.setattr(Database.workspace_users, "get", AsyncMock(return_value=None))

    result = await AuthorizationManager._check_workspace(
        POLICY_RULES["workspace.member.read"],
        _workspace_check(),
        object(),
    )

    assert result.allowed is False
    assert result.reason == enum.AuthorizationDecisionReason.NO_MEMBERSHIP
    assert result.effective_scope == enum.AuthorizationScope.WORKSPACE


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("role", "allowed"),
    [
        (enum.WorkspaceRole.MEMBER, False),
        (enum.WorkspaceRole.ADMIN, True),
        (enum.WorkspaceRole.OWNER, True),
    ],
)
async def test_workspace_decision_enforces_minimum_role(
    monkeypatch: pytest.MonkeyPatch,
    role: enum.WorkspaceRole,
    allowed: bool,
) -> None:
    """Evaluate workspace role ranks against the action minimum."""

    membership = workspace_membership(role=role)
    monkeypatch.setattr(Database.workspace_users, "get", AsyncMock(return_value=membership))

    result = await AuthorizationManager._check_workspace(
        POLICY_RULES["workspace.member.read"],
        _workspace_check(),
        object(),
    )

    assert result.allowed is allowed
    assert result.effective_role == role


@pytest.mark.asyncio
async def test_project_decision_denies_mismatched_parent_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    """Deny a project whose persisted parent workspace differs from the request."""

    monkeypatch.setattr(
        Database.projects,
        "get",
        AsyncMock(return_value=project_dto(workspace_slug="other")),
    )

    result = await AuthorizationManager._check_project(
        POLICY_RULES["project.read"],
        _project_check(),
        object(),
    )

    assert result.allowed is False
    assert result.reason == enum.AuthorizationDecisionReason.SCOPE_MISMATCH


@pytest.mark.asyncio
async def test_project_decision_uses_persisted_project_role(monkeypatch: pytest.MonkeyPatch) -> None:
    """Allow a project read when an effective viewer membership is present."""

    monkeypatch.setattr(Database.projects, "get", AsyncMock(return_value=project_dto()))
    monkeypatch.setattr(
        Database.project_users,
        "get",
        AsyncMock(return_value=project_membership(role=enum.ProjectRole.VIEWER)),
    )

    result = await AuthorizationManager._check_project(
        POLICY_RULES["project.read"],
        _project_check(),
        object(),
    )

    assert result.allowed is True
    assert result.effective_role == enum.ProjectRole.VIEWER
    assert result.effective_scope == enum.AuthorizationScope.PROJECT


@pytest.mark.asyncio
async def test_service_restriction_can_only_narrow_project_role(monkeypatch: pytest.MonkeyPatch) -> None:
    """Apply a lower persisted service role as the effective decision role."""

    monkeypatch.setattr(Database.projects, "get", AsyncMock(return_value=project_dto()))
    monkeypatch.setattr(
        Database.project_users,
        "get",
        AsyncMock(return_value=project_membership(role=enum.ProjectRole.ADMIN)),
    )
    monkeypatch.setattr(
        Database.service_users,
        "get",
        AsyncMock(return_value=service_restriction(role=enum.ProjectRole.MEMBER)),
    )
    data = _project_check(
        "project.service.manage",
        service_id="agent-service",
    )

    result = await AuthorizationManager._check_project(
        POLICY_RULES["project.service.manage"],
        data,
        object(),
    )

    assert result.allowed is False
    assert result.reason == enum.AuthorizationDecisionReason.ROLE_INSUFFICIENT
    assert result.effective_role == enum.ProjectRole.MEMBER
    assert result.effective_scope == enum.AuthorizationScope.SERVICE


@pytest.mark.asyncio
async def test_inconsistent_service_elevation_makes_policy_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fail closed when stored service access exceeds the project role."""

    monkeypatch.setattr(Database.projects, "get", AsyncMock(return_value=project_dto()))
    monkeypatch.setattr(
        Database.project_users,
        "get",
        AsyncMock(return_value=project_membership(role=enum.ProjectRole.MEMBER)),
    )
    monkeypatch.setattr(
        Database.service_users,
        "get",
        AsyncMock(return_value=service_restriction(role=enum.ProjectRole.ADMIN)),
    )

    with pytest.raises(PmsError) as error:
        await AuthorizationManager._check_project(
            POLICY_RULES["project.service.read"],
            _project_check("project.service.read", service_id="agent-service"),
            object(),
        )

    assert error.value.status_code == 503
    assert error.value.code == "POLICY_UNAVAILABLE"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("data", "code"),
    [
        (_project_check(action="unknown.action"), "ACTION_UNKNOWN"),
        (_project_check(user_id=OTHER_USER_ID), "CONSUMER_FORBIDDEN"),
    ],
)
async def test_authorization_check_rejects_unknown_actions_and_other_subjects(
    data: pydantic.AuthorizationCheckRequest,
    code: str,
) -> None:
    """Reject unregistered policies and decisions targeting another user."""

    with pytest.raises(PmsError) as error:
        await AuthorizationManager.check_authorization(user_dto(), data)

    assert error.value.code == code


@pytest.mark.asyncio
async def test_disabled_subject_receives_stable_denial(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return a denial rather than evaluating memberships for a disabled subject."""

    _use_session(monkeypatch, object())
    monkeypatch.setattr(
        Database.users,
        "get",
        AsyncMock(return_value=user_dto(is_active=False)),
    )
    record = Mock()
    monkeypatch.setattr(AuthorizationManager, "_record", record)

    result = await AuthorizationManager.check_authorization(user_dto(), _project_check())

    assert result.allowed is False
    assert result.reason == enum.AuthorizationDecisionReason.USER_DISABLED
    assert result.policy_version == POLICY_VERSION
    record.assert_called_once()


@pytest.mark.asyncio
async def test_last_workspace_owner_cannot_be_revoked(monkeypatch: pytest.MonkeyPatch) -> None:
    """Protect the final persisted workspace owner from membership revocation."""

    _use_session(monkeypatch, object())
    monkeypatch.setattr(
        Database.workspace_users,
        "get_list",
        AsyncMock(return_value=[workspace_membership()]),
    )

    with pytest.raises(PmsError) as error:
        await AuthorizationManager.revoke_workspace_member(
            "workspace",
            USER_ID,
            user_dto(),
            pydantic.RevokeMembershipRequest(expected_version=1),
        )

    assert error.value.code == "LAST_WORKSPACE_OWNER"


@pytest.mark.asyncio
async def test_last_project_admin_cannot_be_revoked(monkeypatch: pytest.MonkeyPatch) -> None:
    """Protect the final persisted project administrator from revocation."""

    _use_session(monkeypatch, object())
    monkeypatch.setattr(Database.projects, "get", AsyncMock(return_value=project_dto()))
    monkeypatch.setattr(
        Database.project_users,
        "get_list",
        AsyncMock(return_value=[project_membership()]),
    )

    with pytest.raises(PmsError) as error:
        await AuthorizationManager.revoke_project_member(
            PROJECT_ID,
            USER_ID,
            user_dto(),
            pydantic.RevokeMembershipRequest(expected_version=1),
        )

    assert error.value.code == "LAST_PROJECT_ADMIN"


@pytest.mark.asyncio
async def test_service_restriction_cannot_elevate_target_role(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reject a service role higher than the target's project membership."""

    actor_membership = project_membership()
    target_membership = project_membership(
        id=OTHER_USER_ID,
        user_id=OTHER_USER_ID,
        role=enum.ProjectRole.MEMBER,
    )
    _use_session(monkeypatch, object())
    monkeypatch.setattr(Database.projects, "get", AsyncMock(return_value=project_dto()))
    monkeypatch.setattr(
        Database.project_users,
        "get_list",
        AsyncMock(return_value=[actor_membership, target_membership]),
    )
    monkeypatch.setattr(
        Database.users,
        "get",
        AsyncMock(return_value=user_dto(id=OTHER_USER_ID)),
    )

    with pytest.raises(PmsError) as error:
        await AuthorizationManager.put_service_restriction(
            PROJECT_ID,
            OTHER_USER_ID,
            "agent-service",
            user_dto(),
            pydantic.PutServiceRestrictionRequest(role=enum.ProjectRole.ADMIN),
        )

    assert error.value.status_code == 422
    assert error.value.code == "SERVICE_ROLE_ELEVATION"


@pytest.mark.asyncio
async def test_bootstrap_must_target_authenticated_creator() -> None:
    """Reject creator bootstrap before database access when subject and actor differ."""

    data = pydantic.BootstrapCreatorAccessRequest(
        workspace_id="workspace",
        creator_user_id=OTHER_USER_ID,
    )

    with pytest.raises(PmsError) as error:
        await AuthorizationManager.bootstrap_creator_access(PROJECT_ID, user_dto(), data)

    assert error.value.status_code == 403
    assert error.value.code == "PMS_CALLER_FORBIDDEN"
