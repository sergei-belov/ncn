"""Unit tests for reusable backend service and model utilities."""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from libs.cp_aiostorage_orm.operation_result import OperationResult, OperationStatus
from libs.cp_common.models.enum import AuthFlow
from libs.cp_common.models.pydantic.api import BulkBaseRequest
from libs.cp_common.models.pydantic.serialized_types import convert_to_dt
from libs.cp_common.services.auth import Authorization
from libs.cp_common.services.base_service_hub import BaseServiceHub
from libs.cp_common.services.names_resolver import NamesResolver
from tests.unit.factories import USER_ID


def test_local_token_round_trip_preserves_identity_claims() -> None:
    """Sign and verify a local token while preserving email and subject claims."""

    authorization = Authorization(
        flow=AuthFlow.LOCAL,
        secret_key="unit-test-secret",
        algorythm="HS256",
        login_url="/login",
        expires_delta=60,
    )

    token = authorization.create_access_token(
        email="user@example.com",
        subject=str(USER_ID),
    )
    payload = authorization.decode_access_token(token)

    assert payload.email == "user@example.com"
    assert payload.sub == str(USER_ID)
    assert payload.exp is not None


def test_password_hash_verification_accepts_only_original_secret() -> None:
    """Verify a generated password hash without exposing the original password."""

    authorization = Authorization(
        flow=AuthFlow.LOCAL,
        secret_key="unit-test-secret",
        algorythm="HS256",
        login_url="/login",
        expires_delta=60,
    )

    password_hash = authorization.get_password_hash("correct-password")

    assert password_hash != "correct-password"
    assert authorization.verify_password("correct-password", password_hash) is True
    assert authorization.verify_password("wrong-password", password_hash) is False


@pytest.mark.asyncio
async def test_service_hub_healthcheck_requires_every_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Report healthy only when every registered external service responds true."""

    services = [
        SimpleNamespace(ping=AsyncMock(return_value=True)),
        SimpleNamespace(ping=AsyncMock(return_value=False)),
    ]

    def get_services(_cls: type[BaseServiceHub]) -> list[SimpleNamespace]:
        """Return deterministic fake services for the aggregate check."""

        return services

    monkeypatch.setattr(
        BaseServiceHub,
        "get_external_services",
        classmethod(get_services),
    )

    assert await BaseServiceHub.healthcheck() is False
    services[0].ping.assert_awaited_once()
    services[1].ping.assert_awaited_once()


@pytest.mark.asyncio
async def test_service_hub_healthcheck_fails_closed_on_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Convert an external-service exception into an unhealthy result."""

    services = [SimpleNamespace(ping=AsyncMock(side_effect=RuntimeError("offline")))]

    def get_services(_cls: type[BaseServiceHub]) -> list[SimpleNamespace]:
        """Return a failing fake service for the aggregate check."""

        return services

    monkeypatch.setattr(
        BaseServiceHub,
        "get_external_services",
        classmethod(get_services),
    )

    assert await BaseServiceHub.healthcheck() is False


def test_name_resolver_increments_highest_existing_copy() -> None:
    """Generate a copied name after the highest matching numeric suffix."""

    resolver = NamesResolver("copy")

    result = resolver.copy(
        "Section",
        ["Section (copy)", "Section (copy 2)", "Other (copy 9)"],
    )

    assert result == "Section (copy 3)"


def test_name_resolver_enumerates_only_exact_base_names() -> None:
    """Ignore unrelated names when selecting the next base-name index."""

    result = NamesResolver.get_new_base_name(
        "task",
        "_",
        ["task_1", "task_7", "task_extra_99", "other_20"],
    )

    assert result == "task_8"


def test_datetime_converter_supports_formatted_and_epoch_values() -> None:
    """Normalize stored datetime strings and millisecond epoch values."""

    formatted = convert_to_dt("2026-01-02 03:04:05")
    epoch = convert_to_dt(0)

    assert formatted == datetime(2026, 1, 2, 3, 4, 5)
    assert epoch.timestamp() == 0


def test_bulk_request_requires_a_selection_strategy() -> None:
    """Reject bulk actions without explicit IDs or selection parameters."""

    with pytest.raises(ValidationError):
        BulkBaseRequest(data={"enabled": True})

    request = BulkBaseRequest(item_ids=[USER_ID], data={"enabled": True})
    assert request.item_ids == [USER_ID]


@pytest.mark.parametrize(
    ("value", "expected_status", "ok"),
    [
        (True, OperationStatus.success, True),
        (False, OperationStatus.failed, False),
    ],
)
def test_storage_operation_result_normalizes_boolean_status(
    value: bool,
    expected_status: OperationStatus,
    ok: bool,
) -> None:
    """Normalize boolean storage results into explicit operation statuses."""

    result = OperationResult(value, message="done")

    assert result.status == expected_status
    assert result.ok is ok
    assert "message=done" in str(result)
