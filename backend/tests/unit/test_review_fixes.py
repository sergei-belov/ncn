import json
from types import SimpleNamespace

import pytest

from api.dependencies.http import reject_unknown_query_params
from api.main import Application
from api.managers.common import PmsError
from api.services import Services


def test_unknown_query_parameter_is_rejected() -> None:
    """Reject query parameters outside a route's explicit allowlist."""

    dependency = reject_unknown_query_params("limit")
    request = SimpleNamespace(query_params={"limit": "10", "unexpected": "value"})

    with pytest.raises(PmsError) as error:
        dependency(request)

    assert error.value.status_code == 400
    assert error.value.code == "MALFORMED_REQUEST"


@pytest.mark.asyncio
async def test_query_validation_error_uses_malformed_request_response() -> None:
    """Map query validation failures to the malformed-request response."""

    request = SimpleNamespace()
    validation_error = SimpleNamespace(
        errors=lambda: [
            {
                "type": "uuid_parsing",
                "loc": ("query", "state_id"),
                "msg": "Input should be a valid UUID",
            }
        ]
    )

    response = await Application.validation_error_handler(request, validation_error)
    payload = json.loads(response.body)

    assert response.status_code == 400
    assert payload["error"]["code"] == "MALFORMED_REQUEST"


@pytest.mark.asyncio
async def test_prometheus_collector_is_healthy_when_constructed() -> None:
    """Treat the in-process Prometheus collector as healthy after creation."""

    assert await Services.collector.ping() is True
