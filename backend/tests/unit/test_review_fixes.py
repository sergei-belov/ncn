import json
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

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


@pytest.mark.asyncio
async def test_domain_error_handler_preserves_structured_context() -> None:
    """Serialize domain error metadata and the request correlation identifier."""

    request = SimpleNamespace(
        state=SimpleNamespace(correlation_id="trace-1"),
        url=SimpleNamespace(path="/api/v1/projects"),
    )
    error = PmsError(
        409,
        "VERSION_CONFLICT",
        "Resource changed.",
        details={"version": 3},
        current={"version": 4},
    )

    response = await Application.pms_error_handler(request, error)
    payload = json.loads(response.body)

    assert response.status_code == 409
    assert payload["error"]["correlation_id"] == "trace-1"
    assert payload["error"]["details"] == {"version": 3}
    assert payload["error"]["current"] == {"version": 4}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "code"),
    [(400, "MALFORMED_REQUEST"), (401, "AUTH_REQUIRED"), (403, "FORBIDDEN"), (404, "PROJECT_NOT_FOUND")],
)
async def test_framework_http_errors_use_public_codes(status_code: int, code: str) -> None:
    """Map common framework status codes to stable public error codes."""

    request = SimpleNamespace(state=SimpleNamespace(correlation_id="trace-2"))

    response = await Application.http_error_handler(
        request,
        HTTPException(status_code=status_code, detail="Failure"),
    )
    payload = json.loads(response.body)

    assert response.status_code == status_code
    assert payload["error"]["code"] == code


@pytest.mark.asyncio
async def test_internal_error_handler_hides_exception_details() -> None:
    """Return a generic response without leaking unexpected exception text."""

    request = SimpleNamespace(
        state=SimpleNamespace(correlation_id="trace-3"),
        url=SimpleNamespace(path="/api/v1/projects"),
    )

    response = await Application.internal_error_handler(request, RuntimeError("secret"))
    payload = json.loads(response.body)

    assert response.status_code == 500
    assert payload["error"]["code"] == "INTERNAL_ERROR"
    assert "secret" not in response.body.decode()


@pytest.mark.asyncio
async def test_correlation_middleware_preserves_valid_client_identifier() -> None:
    """Echo a bounded valid client correlation ID on the response."""

    request = SimpleNamespace(
        headers={"X-Correlation-ID": "client.trace-4"},
        state=SimpleNamespace(),
    )

    async def call_next(_request: object) -> SimpleNamespace:
        """Return a minimal response object accepted by the middleware."""

        return SimpleNamespace(headers={})

    response = await Application.correlation_id_middleware(
        SimpleNamespace(),
        request,
        call_next,
    )

    assert request.state.correlation_id == "client.trace-4"
    assert response.headers["X-Correlation-ID"] == "client.trace-4"
