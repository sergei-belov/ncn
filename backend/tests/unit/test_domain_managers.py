"""Unit tests for project, state, agent, board, work-item, and epic managers."""

from collections import namedtuple
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from api.db import Database
from api.managers.agents import AgentsManager
from api.managers.board import BoardManager
from api.managers.common import PmsError
from api.managers.epics import EpicsManager
from api.managers.projects import ProjectsManager
from api.managers.states import StatesManager
from api.managers.work_items import WorkItemsManager
from models import enum, pydantic
from tests.unit.factories import (
    AGENT_ID,
    EPIC_ID,
    OTHER_USER_ID,
    PROJECT_ID,
    STATE_ID,
    USER_ID,
    WORK_ITEM_ID,
    agent_dto,
    epic_dto,
    project_dto,
    state_dto,
    work_item_dto,
)


@pytest.mark.asyncio
async def test_agent_loader_hides_missing_project_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Map an absent scoped agent to the stable not-found error."""

    monkeypatch.setattr(Database.agents, "get", AsyncMock(return_value=None))

    with pytest.raises(PmsError) as error:
        await AgentsManager._get_agent(object(), PROJECT_ID, AGENT_ID)

    assert error.value.status_code == 404
    assert error.value.code == "AGENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_live_agent_names_are_unique(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reject a name used by another non-archived project agent."""

    monkeypatch.setattr(
        Database.agents,
        "get_list",
        AsyncMock(return_value=[agent_dto(name="Worker")]),
    )

    with pytest.raises(PmsError) as error:
        await AgentsManager._require_unique_live_name(object(), PROJECT_ID, "Worker")

    assert error.value.code == "VALIDATION_ERROR"
    assert "name" in error.value.field_errors


@pytest.mark.asyncio
async def test_archived_agent_name_can_be_reused(monkeypatch: pytest.MonkeyPatch) -> None:
    """Allow a new live agent to reuse an archived agent's name."""

    monkeypatch.setattr(
        Database.agents,
        "get_list",
        AsyncMock(return_value=[agent_dto(status=enum.AgentStatus.ARCHIVED)]),
    )

    await AgentsManager._require_unique_live_name(object(), PROJECT_ID, "Worker")


def test_agent_version_guard_reports_current_version() -> None:
    """Reject stale agent commands with the current persisted version."""

    with pytest.raises(PmsError) as error:
        AgentsManager._require_version(agent_dto(version=4), expected_version=3)

    assert error.value.status_code == 409
    assert error.value.code == "AGENT_VERSION_CONFLICT"
    assert error.value.details == {"version": 4}


@pytest.mark.asyncio
async def test_coordinator_creation_is_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return the existing coordinator without attempting another insert."""

    coordinator = agent_dto(kind=enum.AgentKind.COORDINATOR)
    create = AsyncMock()
    monkeypatch.setattr(Database.agents, "get", AsyncMock(return_value=coordinator))
    monkeypatch.setattr(Database.agents, "create", create)

    result = await AgentsManager.create_coordinator(object(), PROJECT_ID, USER_ID)

    assert result == coordinator
    create.assert_not_awaited()


def test_agent_response_omits_internal_creator_field() -> None:
    """Expose the public agent shape without its internal creator identifier."""

    response = AgentsManager._response(agent_dto())

    assert response.data.id == AGENT_ID
    assert "created_by" not in response.data.model_dump()


def test_state_aggregate_is_converted_with_work_item_count() -> None:
    """Convert a repository aggregate row into the public state representation."""

    state = state_dto()
    StateRow = namedtuple("StateRow", [*state.model_dump().keys(), "work_items_count"])
    row = StateRow(*state.model_dump().values(), 12)

    result = StatesManager._state_api(row)

    assert result.id == STATE_ID
    assert result.work_items_count == 12


@pytest.mark.asyncio
async def test_work_item_assignee_map_preserves_repository_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Group ordered work-item assignee relations by owning item."""

    monkeypatch.setattr(
        Database.work_item_assignees,
        "get_list",
        AsyncMock(
            return_value=[
                SimpleNamespace(work_item_id=WORK_ITEM_ID, user_id=USER_ID),
                SimpleNamespace(work_item_id=WORK_ITEM_ID, user_id=OTHER_USER_ID),
            ]
        ),
    )

    result = await WorkItemsManager._assignee_map(object(), [WORK_ITEM_ID])

    assert result == {WORK_ITEM_ID: [USER_ID, OTHER_USER_ID]}


@pytest.mark.asyncio
async def test_work_item_assignees_are_replaced_as_one_relation_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Delete prior work-item assignees before inserting the requested set."""

    delete_list = AsyncMock()
    bulk_create = AsyncMock()
    monkeypatch.setattr(Database.work_item_assignees, "delete_list", delete_list)
    monkeypatch.setattr(Database.work_item_assignees, "bulk_create", bulk_create)

    await WorkItemsManager._replace_assignees(
        object(),
        WORK_ITEM_ID,
        [USER_ID, OTHER_USER_ID],
    )

    delete_list.assert_awaited_once()
    created = bulk_create.await_args.args[0]
    assert [item.user_id for item in created] == [USER_ID, OTHER_USER_ID]
    assert all(item.work_item_id == WORK_ITEM_ID for item in created)


def test_work_item_card_uses_project_sequence_identifier() -> None:
    """Build the canonical display identifier from project and sequence values."""

    card = WorkItemsManager._card(work_item_dto(), "PRJ", [USER_ID])

    assert card.identifier == "PRJ-7"
    assert card.assignee_ids == [USER_ID]


@pytest.mark.asyncio
async def test_work_item_reference_validation_rejects_foreign_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reject a workflow state absent from the work item's project."""

    monkeypatch.setattr(Database.states, "get", AsyncMock(return_value=None))

    with pytest.raises(PmsError) as error:
        await WorkItemsManager._validate_references(
            object(),
            PROJECT_ID,
            STATE_ID,
            None,
            [],
        )

    assert error.value.code == "CROSS_PROJECT_REFERENCE"


@pytest.mark.asyncio
async def test_epic_assignee_map_returns_empty_entries_without_query(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return an empty mapping for known epics without querying empty input."""

    get_list = AsyncMock()
    monkeypatch.setattr(Database.epic_assignees, "get_list", get_list)

    result = await EpicsManager._assignee_map(object(), [])

    assert result == {}
    get_list.assert_not_awaited()


@pytest.mark.asyncio
async def test_epic_assignees_are_replaced_as_one_relation_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Delete prior epic assignees before inserting the requested set."""

    delete_list = AsyncMock()
    bulk_create = AsyncMock()
    monkeypatch.setattr(Database.epic_assignees, "delete_list", delete_list)
    monkeypatch.setattr(Database.epic_assignees, "bulk_create", bulk_create)

    await EpicsManager._replace_assignees(object(), EPIC_ID, [USER_ID])

    delete_list.assert_awaited_once()
    created = bulk_create.await_args.args[0]
    assert len(created) == 1
    assert created[0].epic_id == EPIC_ID
    assert created[0].user_id == USER_ID


def test_epic_list_item_uses_project_epic_identifier() -> None:
    """Build the canonical epic display identifier and progress values."""

    item = EpicsManager._list_item(epic_dto(), "PRJ", [USER_ID], 5, 2, 40)

    assert item.identifier == "PRJ-E3"
    assert item.work_items_count == 5
    assert item.completed_work_items_count == 2
    assert item.progress_percent == 40


@pytest.mark.asyncio
async def test_epic_full_view_requires_progress_row(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return not found if an epic disappears while its progress is loaded."""

    monkeypatch.setattr(EpicsManager, "_assignee_map", AsyncMock(return_value={EPIC_ID: []}))
    monkeypatch.setattr(Database.epics, "get_with_progress", AsyncMock(return_value=None))

    with pytest.raises(PmsError) as error:
        await EpicsManager._full(object(), epic_dto(), "PRJ")

    assert error.value.code == "EPIC_NOT_FOUND"


@pytest.mark.asyncio
async def test_existing_board_preferences_are_returned_without_write(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reuse persisted board preferences rather than reinitializing them."""

    preferences = pydantic.BoardPreferenceDTO(
        id=USER_ID,
        project_id=PROJECT_ID,
        user_id=USER_ID,
        display={"show_priority": False},
        collapsed_state_ids=[STATE_ID],
        version=2,
    )
    upsert = AsyncMock()
    monkeypatch.setattr(Database.board_preferences, "get", AsyncMock(return_value=preferences))
    monkeypatch.setattr(Database.board_preferences, "upsert", upsert)

    result = await BoardManager._preferences(object(), PROJECT_ID, USER_ID)

    assert result == preferences
    upsert.assert_not_awaited()


@pytest.mark.asyncio
async def test_board_preference_initialization_recovers_concurrent_winner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reload preferences when another request wins lazy initialization."""

    winner = pydantic.BoardPreferenceDTO(
        id=USER_ID,
        project_id=PROJECT_ID,
        user_id=USER_ID,
        display={
            "show_priority": True,
            "show_assignees": True,
            "show_due_date": True,
            "show_epic": True,
        },
        collapsed_state_ids=[],
        version=1,
    )
    get = AsyncMock(side_effect=[None, winner])
    monkeypatch.setattr(Database.board_preferences, "get", get)
    monkeypatch.setattr(Database.board_preferences, "upsert", AsyncMock(return_value=None))

    result = await BoardManager._preferences(object(), PROJECT_ID, USER_ID)

    assert result == winner
    assert get.await_count == 2


@pytest.mark.asyncio
async def test_project_api_requires_default_state() -> None:
    """Reject a malformed project aggregate without a configured default state."""

    with pytest.raises(PmsError) as error:
        await ProjectsManager._project_api(
            object(),
            project_dto(default_state_id=None),
            enum.ProjectRole.ADMIN,
            summaries=[],
            work_items_count=0,
            epics_count=0,
        )

    assert error.value.status_code == 500
    assert error.value.code == "INTERNAL_ERROR"


@pytest.mark.asyncio
async def test_project_api_uses_preloaded_counts_and_role_permissions() -> None:
    """Build a project response from preloaded aggregates without repositories."""

    project = await ProjectsManager._project_api(
        object(),
        project_dto(),
        enum.ProjectRole.MEMBER,
        summaries=[],
        work_items_count=4,
        epics_count=2,
    )

    assert project.id == PROJECT_ID
    assert project.active_work_items_count == 4
    assert project.epics_count == 2
    assert project.permissions.can_create_work_item is True
    assert project.permissions.can_manage_states is False
