from enum import StrEnum


class WorkspaceRole(StrEnum):
    """Workspace membership roles ordered by authority."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class ProjectMembershipSource(StrEnum):
    """Supported origins for a project membership."""

    MANUAL = "manual"
    BOOTSTRAP = "bootstrap"


class AuthorizationScope(StrEnum):
    """Scope families understood by the named authorization policy."""

    WORKSPACE = "workspace"
    PROJECT = "project"
    SERVICE = "service"


class AuthorizationDecisionReason(StrEnum):
    """Stable outcomes returned by named authorization checks."""

    ROLE_ALLOWED = "ROLE_ALLOWED"
    NO_MEMBERSHIP = "NO_MEMBERSHIP"
    ROLE_INSUFFICIENT = "ROLE_INSUFFICIENT"
    USER_DISABLED = "USER_DISABLED"
    SCOPE_MISMATCH = "SCOPE_MISMATCH"
