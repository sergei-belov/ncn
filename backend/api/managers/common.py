import base64
import binascii
import json
import logging
from html import escape
from html.parser import HTMLParser
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.db import Database
from models import enum, pydantic
from models.pydantic.api import common_api


DEFAULT_DISPLAY = {
    "show_priority": True,
    "show_assignees": True,
    "show_due_date": True,
    "show_epic": True,
}
EVENT_LOGGER = logging.getLogger("ncn_pms.events")


def emit_event(name: str, **metadata) -> None:
    """Write a successful domain event to the structured event logger.

    Args:
        name: Event name.
        **metadata: Event fields rendered in stable key order.
    """
    fields = " ".join(f"{key}={value}" for key, value in sorted(metadata.items()))
    EVENT_LOGGER.info("event=%s result=success %s", name, fields)


class PmsError(Exception):
    """Represent a domain failure that maps directly to an API error.

    Attributes:
        status_code: HTTP status returned to the client.
        code: Stable machine-readable error code.
        message: Human-readable error message.
        details: Optional structured error context.
        field_errors: Optional validation failures keyed by field name.
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        *,
        details: dict | None = None,
        field_errors: dict | None = None,
    ):
        """Initialize a domain API error.

        Args:
            status_code: HTTP status returned to the client.
            code: Stable machine-readable error code.
            message: Human-readable error message.
            details: Optional structured error context.
            field_errors: Optional validation failures keyed by field name.
        """
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        self.field_errors = field_errors
        super().__init__(message)


def encode_cursor(offset: int) -> str:
    """Encode a non-secret list offset as a URL-safe cursor.

    Args:
        offset: Offset to encode.

    Returns:
        An unpadded URL-safe base64 cursor.
    """
    payload = json.dumps({"offset": offset}, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(payload).decode().rstrip("=")


def decode_cursor(cursor: str | None) -> int:
    """Decode a URL-safe pagination cursor into its offset.

    Args:
        cursor: Cursor to decode, or ``None`` for the first page.

    Returns:
        The decoded non-negative offset.

    Raises:
        PmsError: If the cursor is malformed or contains an invalid offset.
    """
    if not cursor:
        return 0
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        value = json.loads(base64.urlsafe_b64decode(padded).decode())
        offset = int(value["offset"])
        if offset < 0:
            raise ValueError
        return offset
    except (
        ValueError,
        KeyError,
        TypeError,
        json.JSONDecodeError,
        binascii.Error,
        UnicodeDecodeError,
    ) as exc:
        raise PmsError(400, "MALFORMED_REQUEST", "Invalid cursor.") from exc


def cursor_meta(offset: int, limit: int, returned: int, total: int) -> common_api.CursorMeta:
    """Build cursor metadata for a page of results.

    Args:
        offset: Offset used to fetch the current page.
        limit: Requested page size.
        returned: Number of rows returned on the current page.
        total: Total number of matching rows.

    Returns:
        Metadata containing total count and a cursor for the next page, if any.
    """
    next_offset = offset + returned
    has_more = next_offset < total
    return common_api.CursorMeta(
        next_cursor=encode_cursor(next_offset) if has_more else None,
        has_more=has_more,
        total_count=total,
    )


def parse_uuid_csv(value: str | None, field: str) -> list[UUID]:
    """Parse a comma-separated UUID filter while preserving unique order.

    Args:
        value: Raw comma-separated filter value.
        field: Public field name used in validation errors.

    Returns:
        Unique UUID values in input order.

    Raises:
        PmsError: If any non-empty value is not a valid UUID.
    """
    if not value:
        return []
    try:
        return list(dict.fromkeys(UUID(item.strip()) for item in value.split(",") if item.strip()))
    except ValueError as exc:
        raise PmsError(400, "MALFORMED_REQUEST", f"Invalid {field} filter.") from exc


def parse_enum_csv(value: str | None, enum_type, field: str) -> list:
    """Parse a comma-separated enum filter while preserving unique order.

    Args:
        value: Raw comma-separated filter value.
        enum_type: Enum class used to validate each value.
        field: Public field name used in validation errors.

    Returns:
        Unique enum members in input order.

    Raises:
        PmsError: If any non-empty value is not accepted by the enum.
    """
    if not value:
        return []
    try:
        return list(dict.fromkeys(enum_type(item.strip()) for item in value.split(",") if item.strip()))
    except ValueError as exc:
        raise PmsError(400, "MALFORMED_REQUEST", f"Invalid {field} filter.") from exc


class _SafeHTMLParser(HTMLParser):
    """Collect a conservative allowlist of safe HTML elements and links."""

    allowed_tags = {
        "p", "br", "strong", "em", "u", "s", "blockquote", "code", "pre",
        "ul", "ol", "li", "h1", "h2", "h3", "h4", "a",
    }
    void_tags = {"br"}

    def __init__(self):
        """Initialize an empty sanitized-output buffer."""

        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.blocked_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Append an allowed start tag with sanitized attributes.

        Args:
            tag: Parsed HTML tag name.
            attrs: Parsed attribute name and value pairs.
        """
        tag = tag.casefold()
        if tag in {"script", "style", "iframe", "object"}:
            self.blocked_depth += 1
            return
        if self.blocked_depth or tag not in self.allowed_tags:
            return
        safe_attrs: list[str] = []
        if tag == "a":
            for name, value in attrs:
                if name.casefold() == "href" and value:
                    normalized = value.strip()
                    safe_relative = normalized.startswith("/") and not normalized.startswith("//")
                    if normalized.startswith(("https://", "http://", "mailto:", "#")) or safe_relative:
                        safe_attrs.append(f'href="{escape(normalized, quote=True)}"')
            safe_attrs.extend(['rel="noopener noreferrer"', 'target="_blank"'])
        suffix = f" {' '.join(safe_attrs)}" if safe_attrs else ""
        self.parts.append(f"<{tag}{suffix}>")

    def handle_endtag(self, tag: str) -> None:
        """Append an allowed end tag or leave a blocked element.

        Args:
            tag: Parsed HTML tag name.
        """
        tag = tag.casefold()
        if tag in {"script", "style", "iframe", "object"}:
            self.blocked_depth = max(0, self.blocked_depth - 1)
            return
        if not self.blocked_depth and tag in self.allowed_tags and tag not in self.void_tags:
            self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        """Append escaped text unless it belongs to blocked content.

        Args:
            data: Text encountered by the parser.
        """
        if not self.blocked_depth:
            self.parts.append(escape(data))


def sanitize_html(value: str) -> str:
    """Sanitize rich text and enforce the stored-size limit.

    Args:
        value: Untrusted HTML fragment.

    Returns:
        HTML containing only allowed elements, safe link targets, and escaped
        text content.

    Raises:
        PmsError: If the sanitized UTF-8 payload exceeds 100 KiB.
    """
    parser = _SafeHTMLParser()
    parser.feed(value)
    sanitized = "".join(parser.parts)
    if len(sanitized.encode("utf-8")) > 100 * 1024:
        raise PmsError(422, "VALIDATION_ERROR", "description_html exceeds 100 KiB.")
    return sanitized


def permissions_for(role: enum.ProjectRole) -> common_api.ProjectPermissions:
    """Resolve project capabilities granted to a membership role.

    Args:
        role: Project membership role.

    Returns:
        The explicit permission set granted to that role.
    """
    admin = role == enum.ProjectRole.ADMIN
    editor = role in {enum.ProjectRole.ADMIN, enum.ProjectRole.MEMBER}
    return common_api.ProjectPermissions(
        can_view_project=True,
        can_edit_project=admin,
        can_archive_project=admin,
        can_manage_states=admin,
        can_manage_agents=admin,
        can_create_work_item=editor,
        can_edit_work_item=editor,
        can_move_work_item=editor,
        can_delete_own_work_item=editor,
        can_delete_any_work_item=admin,
        can_create_epic=editor,
        can_edit_epic=editor,
        can_delete_own_epic=editor,
        can_delete_any_epic=admin,
    )


class AccessContext:
    """Bundle a project, membership role, and resolved permissions."""

    def __init__(
        self,
        project: pydantic.ProjectDTO,
        role: enum.ProjectRole,
        permissions: common_api.ProjectPermissions,
    ):
        """Initialize a validated project access context.

        Args:
            project: Project being accessed.
            role: Actor's membership role.
            permissions: Capabilities resolved for the role.
        """
        self.project = project
        self.role = role
        self.permissions = permissions


class AccessManager:
    """Validate workspace, project, and capability access for managers."""

    @staticmethod
    def require_workspace(actor: pydantic.ActorDTO, workspace_slug: str) -> None:
        """Require an actor to belong to the requested workspace.

        Args:
            actor: Request actor context.
            workspace_slug: Workspace required by the operation.

        Raises:
            PmsError: If the actor belongs to a different workspace.
        """
        if actor.workspace_slug != workspace_slug:
            raise PmsError(403, "FORBIDDEN", "Workspace access is required.")

    @staticmethod
    def require_permission(access: AccessContext, permission: str) -> None:
        """Require a named permission in an access context.

        Args:
            access: Validated project access context.
            permission: Permission attribute that must be enabled.

        Raises:
            PmsError: If the permission is not granted.
        """
        if not getattr(access.permissions, permission):
            raise PmsError(403, "FORBIDDEN", "Permission denied.")

    @staticmethod
    def require_writable(access: AccessContext) -> None:
        """Require the accessed project to accept mutations.

        Args:
            access: Validated project access context.

        Raises:
            PmsError: If the project is archived and therefore read-only.
        """
        if access.project.archived_at is not None:
            raise PmsError(403, "FORBIDDEN", "Archived projects are read-only.")

    @staticmethod
    async def require_project(
        session: AsyncSession,
        actor: pydantic.ActorDTO,
        workspace_slug: str,
        project_id: UUID,
        permission: str | None = None,
    ) -> AccessContext:
        """Load a project and validate an actor's membership and capability.

        Args:
            session: Active database session.
            actor: Request actor context.
            workspace_slug: Workspace expected to contain the project.
            project_id: Project being accessed.
            permission: Optional capability required for a mutation.

        Returns:
            A context containing the project, role, and resolved permissions.

        Raises:
            PmsError: If workspace access, project membership, the requested
                permission, or project writability validation fails.
        """
        AccessManager.require_workspace(actor, workspace_slug)
        project = await Database.projects.get(id=project_id, workspace_slug=workspace_slug, session=session)
        if not project:
            raise PmsError(404, "PROJECT_NOT_FOUND", "Project not found.")
        membership = await Database.project_users.get(
            project_id=project_id, user_id=actor.id, session=session
        )
        if membership:
            role = membership.role
        else:
            raise PmsError(404, "PROJECT_NOT_FOUND", "Project not found.")
        permissions = permissions_for(role)
        access = AccessContext(project, role, permissions)
        if permission:
            AccessManager.require_permission(access, permission)
            AccessManager.require_writable(access)
        return access

    @staticmethod
    async def validate_members(
        session: AsyncSession, project_id: UUID, user_ids: list[UUID]
    ) -> None:
        """Validate that a bounded set of assignees belongs to a project.

        Args:
            session: Active database session.
            project_id: Project that must contain the users.
            user_ids: Assignee identifiers to validate.

        Raises:
            PmsError: If there are too many assignees, duplicates are present,
                or any user is not a project member.
        """
        if len(user_ids) > 10:
            raise PmsError(422, "VALIDATION_ERROR", "At most 10 assignees are allowed.")
        if len(set(user_ids)) != len(user_ids):
            raise PmsError(422, "VALIDATION_ERROR", "Assignees must be unique.")
        if not user_ids:
            return
        memberships = await Database.project_users.get_list(
            project_id=project_id, user_id=user_ids, session=session
        )
        if {member.user_id for member in memberships} != set(user_ids):
            raise PmsError(422, "CROSS_PROJECT_REFERENCE", "Assignee is not a project user.")


async def member_summaries(session: AsyncSession, project_id: UUID) -> list[common_api.MemberSummary]:
    """Return public member summaries for a project.

    Args:
        session: Active database session.
        project_id: Project whose members are requested.

    Returns:
        Member summaries ordered by the repository query.
    """
    members = await Database.project_users.get_members_with_details(
        project_ids=[project_id], session=session
    )
    return [
        common_api.MemberSummary(
            id=member.user_id,
            display_name=member.display_name,
            avatar_url=member.avatar_url,
            is_active=member.is_active,
        )
        for member in members
    ]
