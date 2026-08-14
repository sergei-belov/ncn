"""Deterministic object factories shared by backend unit tests."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from models import enum, pydantic


NOW = datetime(2026, 1, 2, 3, 4, tzinfo=UTC)
USER_ID = UUID("00000000-0000-0000-0000-000000000001")
OTHER_USER_ID = UUID("00000000-0000-0000-0000-000000000002")
PROJECT_ID = UUID("00000000-0000-0000-0000-000000000010")
STATE_ID = UUID("00000000-0000-0000-0000-000000000020")
WORK_ITEM_ID = UUID("00000000-0000-0000-0000-000000000030")
EPIC_ID = UUID("00000000-0000-0000-0000-000000000040")
AGENT_ID = UUID("00000000-0000-0000-0000-000000000050")
MEMBERSHIP_ID = UUID("00000000-0000-0000-0000-000000000060")
WORKSPACE_MEMBERSHIP_ID = UUID("00000000-0000-0000-0000-000000000070")
SERVICE_RESTRICTION_ID = UUID("00000000-0000-0000-0000-000000000080")


class AsyncContext:
    """Expose a value through an asynchronous context-manager protocol."""

    def __init__(self, value: Any):
        """Store the value returned when the context is entered."""

        self.value = value

    async def __aenter__(self) -> Any:
        """Return the stored context value."""

        return self.value

    async def __aexit__(self, *_args: object) -> None:
        """Leave the context without suppressing exceptions."""


def user_dto(**overrides: Any) -> pydantic.UserDTO:
    """Build an active application user with deterministic values."""

    values = {
        "id": USER_ID,
        "email": "user@example.com",
        "name": "Test User",
        "password_hash": None,
        "is_active": True,
        "created_at": NOW,
        "updated_at": NOW,
    }
    values.update(overrides)
    return pydantic.UserDTO(**values)


def project_dto(**overrides: Any) -> pydantic.ProjectDTO:
    """Build a live project with a configured default state."""

    values = {
        "id": PROJECT_ID,
        "workspace_slug": "workspace",
        "name": "Project",
        "identifier": "PRJ",
        "description": None,
        "icon": {"type": "initial", "value": "P"},
        "color": "#112233",
        "access": enum.ProjectAccess.PRIVATE,
        "default_state_id": STATE_ID,
        "archived_at": None,
        "board_version": 1,
        "next_work_item_sequence": 2,
        "next_epic_sequence": 2,
        "created_by": USER_ID,
        "created_at": NOW,
        "updated_at": NOW,
        "version": 1,
    }
    values.update(overrides)
    return pydantic.ProjectDTO(**values)


def project_membership(**overrides: Any) -> pydantic.ProjectUserDTO:
    """Build a project administrator membership."""

    values = {
        "id": MEMBERSHIP_ID,
        "project_id": PROJECT_ID,
        "workspace_id": "workspace",
        "user_id": USER_ID,
        "role": enum.ProjectRole.ADMIN,
        "source": enum.ProjectMembershipSource.MANUAL,
        "version": 1,
        "created_at": NOW,
        "updated_at": NOW,
    }
    values.update(overrides)
    return pydantic.ProjectUserDTO(**values)


def workspace_membership(**overrides: Any) -> pydantic.WorkspaceUserDTO:
    """Build a workspace owner membership."""

    values = {
        "id": WORKSPACE_MEMBERSHIP_ID,
        "workspace_id": "workspace",
        "user_id": USER_ID,
        "role": enum.WorkspaceRole.OWNER,
        "version": 1,
        "created_at": NOW,
        "updated_at": NOW,
    }
    values.update(overrides)
    return pydantic.WorkspaceUserDTO(**values)


def service_restriction(**overrides: Any) -> pydantic.ServiceUserDTO:
    """Build a service-level member restriction."""

    values = {
        "id": SERVICE_RESTRICTION_ID,
        "project_user_id": MEMBERSHIP_ID,
        "service_id": "agent-service",
        "role": enum.ProjectRole.MEMBER,
        "version": 1,
        "created_at": NOW,
        "updated_at": NOW,
    }
    values.update(overrides)
    return pydantic.ServiceUserDTO(**values)


def actor_dto(**overrides: Any) -> pydantic.ActorDTO:
    """Build a workspace-scoped request actor."""

    values = {
        "id": USER_ID,
        "workspace_slug": "workspace",
        "display_name": "Test User",
    }
    values.update(overrides)
    return pydantic.ActorDTO(**values)


def state_dto(**overrides: Any) -> pydantic.ProjectStateDTO:
    """Build a default unstarted workflow state."""

    values = {
        "id": STATE_ID,
        "project_id": PROJECT_ID,
        "name": "Ready",
        "color": "#112233",
        "group": enum.StateGroup.UNSTARTED,
        "position": 0,
        "is_default": True,
        "version": 1,
    }
    values.update(overrides)
    return pydantic.ProjectStateDTO(**values)


def work_item_dto(**overrides: Any) -> pydantic.WorkItemDTO:
    """Build a persisted work item."""

    values = {
        "id": WORK_ITEM_ID,
        "project_id": PROJECT_ID,
        "sequence_id": 7,
        "title": "Unit test",
        "description_html": "<p>description</p>",
        "state_id": STATE_ID,
        "priority": enum.Priority.MEDIUM,
        "epic_id": None,
        "start_date": None,
        "due_date": None,
        "rank": "00000000000000000000000000001024",
        "created_by": USER_ID,
        "created_at": NOW,
        "updated_at": NOW,
        "version": 1,
    }
    values.update(overrides)
    return pydantic.WorkItemDTO(**values)


def epic_dto(**overrides: Any) -> pydantic.EpicDTO:
    """Build a persisted epic."""

    values = {
        "id": EPIC_ID,
        "project_id": PROJECT_ID,
        "sequence_id": 3,
        "title": "Epic",
        "description_html": "<p>description</p>",
        "state_id": STATE_ID,
        "priority": enum.Priority.HIGH,
        "start_date": None,
        "due_date": None,
        "rank": "00000000000000000000000000001024",
        "created_by": USER_ID,
        "created_at": NOW,
        "updated_at": NOW,
        "version": 1,
    }
    values.update(overrides)
    return pydantic.EpicDTO(**values)


def agent_dto(**overrides: Any) -> pydantic.AgentDTO:
    """Build an active worker agent."""

    values = {
        "id": AGENT_ID,
        "project_id": PROJECT_ID,
        "kind": enum.AgentKind.WORKER,
        "name": "Worker",
        "description": "A worker",
        "instructions": "Perform the assigned project work carefully.",
        "model": "qwen3:32b",
        "memory_policy": enum.AgentMemoryPolicy.PROJECT,
        "max_steps_per_run": 25,
        "approval_mode": enum.AgentApprovalMode.PROJECT,
        "status": enum.AgentStatus.ACTIVE,
        "system_tool_names": ["task-management"],
        "created_by": USER_ID,
        "created_at": NOW,
        "updated_at": NOW,
        "version": 1,
    }
    values.update(overrides)
    return pydantic.AgentDTO(**values)
