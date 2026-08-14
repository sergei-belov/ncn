from enum import StrEnum


class ProjectRole(StrEnum):
    """Project membership roles ordered by their intended capability level."""

    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class ProjectAccess(StrEnum):
    """Visibility scopes supported by a project."""

    PRIVATE = "private"
    WORKSPACE = "workspace"


class Priority(StrEnum):
    """Priority values shared by work items and epics."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class StateGroup(StrEnum):
    """Semantic groups used to categorize workflow states."""

    BACKLOG = "backlog"
    UNSTARTED = "unstarted"
    STARTED = "started"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectStatus(StrEnum):
    """Lifecycle statuses accepted by project listing filters."""

    ACTIVE = "active"
    ARCHIVED = "archived"


class DueStatus(StrEnum):
    """Derived due-date categories used by work-item filters."""

    OVERDUE = "overdue"
    DUE_SOON = "due_soon"
    NO_DUE_DATE = "no_due_date"


class EpicStatus(StrEnum):
    """Derived completion statuses used by epic filters."""

    ACTIVE = "active"
    COMPLETED = "completed"


class AgentKind(StrEnum):
    """Functional kinds of agents attached to a project."""

    COORDINATOR = "coordinator"
    WORKER = "worker"


class AgentStatus(StrEnum):
    """Lifecycle statuses for project agents."""

    ACTIVE = "active"
    DISABLED = "disabled"
    ARCHIVED = "archived"


class AgentMemoryPolicy(StrEnum):
    """Scopes under which an agent may retain memory."""

    PROJECT = "project"
    SESSION = "session"
    NONE = "none"


class AgentApprovalMode(StrEnum):
    """Approval policies governing agent execution."""

    PROJECT = "project"
    ALWAYS = "always"
