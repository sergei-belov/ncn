import logging
import re
from collections import defaultdict
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from api.managers.common import PmsError
from api.router.router import router as api_router
from api.services import Services
from api.settings import ConstSettings


class Application(FastAPI):
    """Configure the ncn-pms FastAPI application and its integrations."""

    def __init__(self):
        """Initialize the application, service hub, and HTTP configuration."""

        self.logger = logging.getLogger(__name__)
        self.services = Services()
        super().__init__(
            title=ConstSettings.TITLE,
            description=ConstSettings.DESCRIPTION,
            root_path=Services.config.APP_ROOT_PATH,
        )
        self._configure()

    def _configure(self) -> None:
        """Register middleware, routes, lifecycle hooks, and error handlers."""

        self.middleware("http")(self.correlation_id_middleware)
        if Services.config.CORS_ALLOW_ORIGINS:
            self.add_middleware(
                CORSMiddleware,
                allow_origins=Services.config.CORS_ALLOW_ORIGINS,
                allow_credentials=True,
                allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                allow_headers=[
                    "Authorization",
                    "Content-Type",
                    "X-Correlation-ID",
                ],
                expose_headers=["X-Correlation-ID"],
            )
        self.include_router(api_router)
        for service in self.services.get_external_services():
            self.router.add_event_handler("startup", service.start)
            self.router.add_event_handler("shutdown", service.stop)
        self.add_exception_handler(PmsError, self.pms_error_handler)
        self.add_exception_handler(RequestValidationError, self.validation_error_handler)
        self.add_exception_handler(HTTPException, self.http_error_handler)
        self.add_exception_handler(Exception, self.internal_error_handler)
        self.services.configure_logging()
        self.services.collector.add_instrumentator_to_app(self)

    async def correlation_id_middleware(self, request: Request, call_next):
        """Attach one bounded diagnostic correlation ID to every response.

        Args:
            request: Current HTTP request.
            call_next: Downstream ASGI request handler.

        Returns:
            Downstream response with ``X-Correlation-ID`` set.
        """

        supplied = request.headers.get("X-Correlation-ID", "")
        if re.fullmatch(r"[A-Za-z0-9._:-]{1,128}", supplied):
            correlation_id = supplied
        else:
            correlation_id = str(uuid4())
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response

    @staticmethod
    async def pms_error_handler(request: Request, exc: PmsError) -> JSONResponse:
        """Convert a domain ``PmsError`` into the public error envelope.

        Args:
            request: Request that raised the error.
            exc: Domain error to serialize.

        Returns:
            JSON response with the error's status, code, and optional details.
        """
        error = {
            "code": exc.code,
            "message": exc.message,
            "correlation_id": getattr(getattr(request, "state", None), "correlation_id", None),
        }
        if exc.field_errors:
            error["field_errors"] = exc.field_errors
        if exc.details:
            error["details"] = exc.details
        if exc.current:
            error["current"] = exc.current
        path = getattr(getattr(request, "url", None), "path", "")
        if (
            path.endswith("/authorization/check")
            or "/members" in path
            or path.endswith("/creator-access")
        ):
            logging.getLogger("ncn_authz.events").info(
                "operation=http_request result=error reason=%s correlation_id=%s path=%s",
                exc.code,
                getattr(getattr(request, "state", None), "correlation_id", None),
                path,
            )
            Services.collector.record_authorization(
                operation="http_request",
                result="error",
                reason=exc.code,
            )
        headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder({"error": error}),
            headers=headers,
        )

    @staticmethod
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Convert FastAPI validation failures into field-oriented API errors.

        Args:
            request: Request that failed validation.
            exc: Validation error reported by FastAPI.

        Returns:
            A 400 response for malformed query input or a 422 response for
            other validation failures.
        """
        malformed_query = any(
            error.get("loc", [None])[0] == "query"
            for error in exc.errors()
        )
        code = "MALFORMED_REQUEST" if malformed_query else "VALIDATION_ERROR"
        status_code = (
            status.HTTP_400_BAD_REQUEST
            if malformed_query
            else status.HTTP_422_UNPROCESSABLE_CONTENT
        )
        fields: dict[str, list[dict[str, str]]] = defaultdict(list)
        for error in exc.errors():
            location = error.get("loc", [])
            field = ".".join(str(part) for part in location[1:]) or "request"
            fields[field].append(
                {
                    "code": error.get("type", "INVALID"),
                    "message": error.get("msg", "Invalid value"),
                }
            )
        path = getattr(getattr(request, "url", None), "path", "")
        if path.endswith("/authorization/check") or "/members" in path or path.endswith(
            "/creator-access"
        ):
            Services.collector.record_authorization(
                operation="http_request",
                result="error",
                reason=code,
            )
        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(
                {
                    "error": {
                        "code": code,
                        "message": "The request contains invalid fields.",
                        "correlation_id": getattr(
                            getattr(request, "state", None),
                            "correlation_id",
                            None,
                        ),
                        "field_errors": fields,
                    }
                }
            ),
        )

    @staticmethod
    async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Convert framework HTTP exceptions into the public error envelope.

        Args:
            request: Request that raised the exception.
            exc: Framework HTTP exception to serialize.

        Returns:
            JSON response preserving the exception status code.
        """
        code = "MALFORMED_REQUEST" if exc.status_code == 400 else "INTERNAL_ERROR"
        if exc.status_code == 404:
            code = "PROJECT_NOT_FOUND"
        elif exc.status_code == 401:
            code = "AUTH_REQUIRED"
        elif exc.status_code == 403:
            code = "FORBIDDEN"
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": code,
                    "message": str(exc.detail),
                    "correlation_id": getattr(
                        getattr(request, "state", None),
                        "correlation_id",
                        None,
                    ),
                }
            },
        )

    @staticmethod
    async def internal_error_handler(request: Request, _exc: Exception) -> JSONResponse:
        """Return and safely record an unexpected server exception.

        Args:
            request: Request that raised the exception.
            _exc: Unexpected exception hidden from the client.

        Returns:
            A generic HTTP 500 JSON response.
        """
        path = getattr(getattr(request, "url", None), "path", "")
        if path.endswith("/authorization/check") or "/members" in path or path.endswith(
            "/creator-access"
        ):
            logging.getLogger("ncn_authz.events").error(
                "operation=http_request result=error reason=INTERNAL_ERROR "
                "correlation_id=%s path=%s",
                getattr(getattr(request, "state", None), "correlation_id", None),
                path,
            )
            Services.collector.record_authorization(
                operation="http_request",
                result="error",
                reason="INTERNAL_ERROR",
            )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Unexpected server error.",
                    "correlation_id": getattr(
                        getattr(request, "state", None),
                        "correlation_id",
                        None,
                    ),
                }
            },
        )


app = Application()
