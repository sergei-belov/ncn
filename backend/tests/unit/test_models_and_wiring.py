"""Unit tests for strict API models and application component registration."""

from collections.abc import Callable
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from api.db import Database
from api.managers import Managers
from api.managers.agents import AgentsManager
from api.managers.auth import AuthManager
from api.managers.authorization import AuthorizationManager
from api.managers.board import BoardManager
from api.managers.epics import EpicsManager
from api.managers.projects import ProjectsManager
from api.managers.states import StatesManager
from api.managers.work_items import WorkItemsManager
from api.router.agents import router as agents_router
from api.router.auth import router as auth_router
from api.router.authorization import router as authorization_router
from api.router.board import router as board_router
from api.router.epics import router as epics_router
from api.router.projects import router as projects_router
from api.router.router import router as root_router
from api.router.states import router as states_router
from api.router.work_items import router as work_items_router
from api.settings import ConstSettings, _Settings, get_settings
from models import enum, pydantic
from tests.unit.factories import (
    OTHER_USER_ID,
    PROJECT_ID,
    STATE_ID,
    USER_ID,
    WORK_ITEM_ID,
)


def test_registration_normalizes_identity_fields() -> None:
    """Normalize registration email and display name at the API boundary."""

    request = pydantic.PostRegisterRequest(
        email="  User@Example.COM ",
        name="  Display Name  ",
        password="long-password",
    )

    assert request.email == "user@example.com"
    assert request.name == "Display Name"


def test_api_models_forbid_unknown_fields() -> None:
    """Reject fields outside each public request contract."""

    with pytest.raises(ValidationError):
        pydantic.ProjectListQueries(limit=10, unexpected=True)


def test_runtime_settings_enforce_positive_operational_limits() -> None:
    """Reject non-positive rate, pool, timeout, and token lifetime settings."""

    for field in (
        "RATE_LIMIT_PER_MINUTE",
        "DB_POOL_SIZE",
        "DB_STATEMENT_TIMEOUT_SEC",
        "AUTH_ACCESS_TOKEN_EXPIRE_SECONDS",
    ):
        with pytest.raises(ValidationError):
            _Settings(**{field: 0})


def test_settings_cache_and_service_metadata_are_stable() -> None:
    """Reuse one runtime settings object and expose bounded service metadata."""

    assert get_settings() is get_settings()
    assert ConstSettings.SERVICE == "ncn-pms"
    assert ConstSettings.TITLE


@pytest.mark.parametrize(
    "model_call",
    [
        lambda: pydantic.CreateWorkItemRequest(
            id=WORK_ITEM_ID,
            title="Item",
            before_work_item_id=USER_ID,
            after_work_item_id=OTHER_USER_ID,
        ),
        lambda: pydantic.UpdateWorkItemRequest(
            start_date=date(2026, 2, 2),
            due_date=date(2026, 2, 1),
        ),
        lambda: pydantic.UpdateEpicRequest(
            start_date=date(2026, 2, 2),
            due_date=date(2026, 2, 1),
        ),
    ],
)
def test_entity_models_reject_invalid_ordering_and_dates(
    model_call: Callable[[], object],
) -> None:
    """Reject conflicting rank anchors and reversed entity date ranges."""

    with pytest.raises(ValidationError):
        model_call()


@pytest.mark.parametrize(
    "model_call",
    [
        lambda: pydantic.UpdateStateRequest(name=None),
        lambda: pydantic.UpdateAgentRequest(expected_version=1, name=None),
        lambda: pydantic.UpdateBoardPreferencesRequest(display=None),
        lambda: pydantic.UpdateProjectRequest(color=None),
        lambda: pydantic.UpdateWorkItemRequest(priority=None),
        lambda: pydantic.UpdateEpicRequest(state_id=None),
    ],
)
def test_partial_updates_reject_null_for_non_nullable_fields(
    model_call: Callable[[], object],
) -> None:
    """Distinguish omitted fields from explicit nulls in partial updates."""

    with pytest.raises(ValidationError):
        model_call()


def test_nullable_update_fields_can_be_explicitly_cleared() -> None:
    """Allow the documented nullable project, work-item, and epic fields to clear."""

    project = pydantic.UpdateProjectRequest(description=None)
    work_item = pydantic.UpdateWorkItemRequest(epic_id=None, due_date=None)
    epic = pydantic.UpdateEpicRequest(due_date=None)

    assert project.model_dump(exclude_unset=True) == {"description": None}
    assert work_item.model_dump(exclude_unset=True) == {"epic_id": None, "due_date": None}
    assert epic.model_dump(exclude_unset=True) == {"due_date": None}


@pytest.mark.parametrize("service_id", ["Agent-Service", "bad service", "_private"])
def test_authorization_request_rejects_invalid_service_identifier(service_id: str) -> None:
    """Accept only bounded lowercase service identifiers at the policy boundary."""

    with pytest.raises(ValidationError):
        pydantic.AuthorizationCheckRequest(
            user_id=USER_ID,
            action="project.service.read",
            workspace_id="workspace",
            project_id=PROJECT_ID,
            service_id=service_id,
            resource={"type": "project", "id": str(PROJECT_ID)},
        )


def test_valid_state_and_agent_payloads_normalize_text() -> None:
    """Trim user-controlled state and agent text at the API boundary."""

    state = pydantic.CreateStateRequest(
        id=STATE_ID,
        name="  Ready  ",
        color="#aabbcc",
        group=enum.StateGroup.UNSTARTED,
    )
    agent = pydantic.CreateAgentRequest(
        name="  Worker  ",
        description="  Description  ",
        instructions="  Perform assigned project tasks carefully.  ",
        model="  qwen3:32b  ",
        memory_policy=enum.AgentMemoryPolicy.PROJECT,
        max_steps_per_run=10,
        approval_mode=enum.AgentApprovalMode.PROJECT,
    )

    assert state.name == "Ready"
    assert agent.name == "Worker"
    assert agent.model == "qwen3:32b"


def test_manager_hub_registers_every_domain_manager() -> None:
    """Expose one manager instance for every backend domain area."""

    expected = {
        "auth": AuthManager,
        "authorization": AuthorizationManager,
        "projects": ProjectsManager,
        "states": StatesManager,
        "agents": AgentsManager,
        "work_items": WorkItemsManager,
        "board": BoardManager,
        "epics": EpicsManager,
    }

    for name, manager_type in expected.items():
        assert isinstance(getattr(Managers, name), manager_type)


def test_database_hub_registers_every_repository() -> None:
    """Expose repositories required by all manager workflows."""

    names = {
        "users",
        "projects",
        "project_users",
        "workspace_users",
        "service_users",
        "states",
        "agents",
        "work_items",
        "work_item_assignees",
        "epics",
        "epic_assignees",
        "board_preferences",
    }

    assert all(getattr(Database, name, None) is not None for name in names)


def test_root_router_registers_all_public_api_areas() -> None:
    """Keep authentication, authorization, and every PMS domain mounted."""

    expected_routers = (
        auth_router,
        authorization_router,
        projects_router,
        agents_router,
        states_router,
        work_items_router,
        board_router,
        epics_router,
    )
    included_routers = [
        getattr(route, "original_router", None)
        for route in root_router.routes
    ]

    assert all(
        any(included is expected for included in included_routers)
        for expected in expected_routers
    )


def test_backend_source_never_uses_database_row_locks() -> None:
    """Enforce the project-wide prohibition on explicit row-lock queries."""

    backend_root = Path(__file__).parents[2]
    forbidden_call = "with_" + "for_update"
    offenders = []
    for source_root in ("api", "models", "libs"):
        for path in (backend_root / source_root).rglob("*.py"):
            if forbidden_call in path.read_text(encoding="utf-8"):
                offenders.append(str(path.relative_to(backend_root)))

    assert offenders == []
