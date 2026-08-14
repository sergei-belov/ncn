"""Unit tests for shared parsing, security, access, and ranking helpers."""

from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from api.db import Database
from api.db.work_items import RANK_WIDTH, format_rank
from api.managers.common import (
    AccessContext,
    AccessManager,
    PmsError,
    cursor_meta,
    decode_cursor,
    encode_cursor,
    parse_enum_csv,
    parse_uuid_csv,
    permissions_for,
    sanitize_html,
)
from models import enum
from tests.unit.factories import OTHER_USER_ID, PROJECT_ID, USER_ID, actor_dto, project_dto


def test_cursor_round_trip_and_first_page_default() -> None:
    """Encode offsets losslessly and default an absent cursor to zero."""

    assert decode_cursor(encode_cursor(123)) == 123
    assert decode_cursor(None) == 0


@pytest.mark.parametrize("cursor", ["not-base64", encode_cursor(-1), "e30"])
def test_invalid_cursor_is_rejected(cursor: str) -> None:
    """Reject malformed, incomplete, and negative cursor payloads."""

    with pytest.raises(PmsError) as error:
        decode_cursor(cursor)

    assert error.value.status_code == 400
    assert error.value.code == "MALFORMED_REQUEST"


def test_cursor_metadata_reports_remaining_rows() -> None:
    """Expose a next cursor only when matching rows remain."""

    page = cursor_meta(offset=10, limit=5, returned=5, total=18)
    final_page = cursor_meta(offset=15, limit=5, returned=3, total=18)

    assert page.has_more is True
    assert decode_cursor(page.next_cursor) == 15
    assert final_page.has_more is False
    assert final_page.next_cursor is None


def test_uuid_csv_preserves_unique_input_order() -> None:
    """Parse UUID filters while removing duplicates in stable order."""

    value = f"{USER_ID}, {OTHER_USER_ID},{USER_ID}"

    assert parse_uuid_csv(value, "assignee_id") == [USER_ID, OTHER_USER_ID]
    assert parse_uuid_csv(None, "assignee_id") == []


def test_invalid_uuid_csv_is_rejected() -> None:
    """Map an invalid UUID filter to a malformed-request error."""

    with pytest.raises(PmsError) as error:
        parse_uuid_csv("not-a-uuid", "assignee_id")

    assert error.value.code == "MALFORMED_REQUEST"


def test_enum_csv_preserves_unique_input_order() -> None:
    """Parse enum filters while removing duplicates in stable order."""

    result = parse_enum_csv("high, low,high", enum.Priority, "priority")

    assert result == [enum.Priority.HIGH, enum.Priority.LOW]


def test_invalid_enum_csv_is_rejected() -> None:
    """Map an unsupported enum filter to a malformed-request error."""

    with pytest.raises(PmsError) as error:
        parse_enum_csv("critical", enum.Priority, "priority")

    assert error.value.code == "MALFORMED_REQUEST"


def test_html_sanitizer_blocks_executable_content_and_unsafe_links() -> None:
    """Keep safe markup while removing scripts, handlers, and unsafe URLs."""

    result = sanitize_html(
        '<p onclick="run()">Hello &amp; bye</p>'
        '<script>alert(1)</script>'
        '<a href="javascript:alert(1)">bad</a>'
        '<a href="https://example.com?a=1&b=2">safe</a>'
    )

    assert result == (
        "<p>Hello &amp; bye</p>"
        '<a rel="noopener noreferrer" target="_blank">bad</a>'
        '<a href="https://example.com?a=1&amp;b=2" '
        'rel="noopener noreferrer" target="_blank">safe</a>'
    )


def test_html_sanitizer_enforces_stored_byte_limit() -> None:
    """Reject sanitized rich text larger than one hundred KiB."""

    with pytest.raises(PmsError) as error:
        sanitize_html("x" * (100 * 1024 + 1))

    assert error.value.status_code == 422
    assert error.value.code == "VALIDATION_ERROR"


def test_project_permissions_follow_role_capabilities() -> None:
    """Grant editing to members and administration only to admins."""

    viewer = permissions_for(enum.ProjectRole.VIEWER)
    member = permissions_for(enum.ProjectRole.MEMBER)
    admin = permissions_for(enum.ProjectRole.ADMIN)

    assert viewer.can_view_project is True
    assert viewer.can_create_work_item is False
    assert member.can_create_work_item is True
    assert member.can_manage_states is False
    assert admin.can_manage_states is True
    assert admin.can_delete_any_epic is True


def test_access_guards_reject_wrong_workspace_permission_and_archive() -> None:
    """Reject mismatched workspaces, missing capabilities, and archived writes."""

    actor = actor_dto()
    viewer_access = AccessContext(
        project_dto(),
        enum.ProjectRole.VIEWER,
        permissions_for(enum.ProjectRole.VIEWER),
    )
    archived_access = AccessContext(
        project_dto(archived_at=project_dto().updated_at),
        enum.ProjectRole.ADMIN,
        permissions_for(enum.ProjectRole.ADMIN),
    )

    with pytest.raises(PmsError, match="Workspace access"):
        AccessManager.require_workspace(actor, "other")
    with pytest.raises(PmsError, match="Permission denied"):
        AccessManager.require_permission(viewer_access, "can_edit_project")
    with pytest.raises(PmsError, match="read-only"):
        AccessManager.require_writable(archived_access)


@pytest.mark.asyncio
async def test_project_access_requires_persisted_membership(monkeypatch: pytest.MonkeyPatch) -> None:
    """Hide an existing project when the actor has no project membership."""

    monkeypatch.setattr(Database.projects, "get", AsyncMock(return_value=project_dto()))
    monkeypatch.setattr(Database.project_users, "get", AsyncMock(return_value=None))

    with pytest.raises(PmsError) as error:
        await AccessManager.require_project(object(), actor_dto(), "workspace", PROJECT_ID)

    assert error.value.status_code == 404
    assert error.value.code == "PROJECT_NOT_FOUND"


@pytest.mark.asyncio
async def test_member_validation_accepts_exact_project_members(monkeypatch: pytest.MonkeyPatch) -> None:
    """Accept a unique bounded assignee list fully represented by memberships."""

    get_list = AsyncMock(
        return_value=[SimpleNamespace(user_id=USER_ID), SimpleNamespace(user_id=OTHER_USER_ID)]
    )
    monkeypatch.setattr(Database.project_users, "get_list", get_list)

    await AccessManager.validate_members(object(), PROJECT_ID, [USER_ID, OTHER_USER_ID])

    get_list.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("user_ids", "code"),
    [
        ([USER_ID, USER_ID], "VALIDATION_ERROR"),
        ([USER_ID] * 11, "VALIDATION_ERROR"),
    ],
)
async def test_member_validation_rejects_invalid_cardinality(
    user_ids: list[UUID],
    code: str,
) -> None:
    """Reject duplicate assignees and assignee lists beyond the domain limit."""

    with pytest.raises(PmsError) as error:
        await AccessManager.validate_members(object(), PROJECT_ID, user_ids)

    assert error.value.code == code


@pytest.mark.asyncio
async def test_member_validation_rejects_cross_project_user(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reject an assignee absent from the project's membership set."""

    monkeypatch.setattr(Database.project_users, "get_list", AsyncMock(return_value=[]))

    with pytest.raises(PmsError) as error:
        await AccessManager.validate_members(object(), PROJECT_ID, [USER_ID])

    assert error.value.code == "CROSS_PROJECT_REFERENCE"


def test_rank_format_is_fixed_width_and_lexically_ordered() -> None:
    """Format numeric ranks so their lexical and numeric ordering agree."""

    low = format_rank(1024)
    high = format_rank(2048)

    assert len(low) == RANK_WIDTH
    assert low < high
