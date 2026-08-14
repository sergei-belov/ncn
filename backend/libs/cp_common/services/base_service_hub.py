import inspect
import logging
from typing import Type

from fastapi import APIRouter
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
)

from libs.cp_common.models.enum import Service
from libs.cp_common.services.base import BaseService


class BaseServiceHub:
    """Discover external services and expose common operational routers."""

    logger: logging.Logger = logging.getLogger(__name__)
    log_level: logging.INFO | logging.DEBUG | logging.ERROR | logging.CRITICAL | logging.WARNING = logging.INFO
    logging_format: str = "%(asctime)s [%(name)s:%(lineno)s] [%(levelname)s]: %(message)s"

    @classmethod
    def get_external_services(cls) -> list[Type[BaseService]]:
        """
        Find all class attributes with BaseService subclass
        for using start and stop methods.
        """
        external_services = []
        for _, obj in inspect.getmembers(cls):
            if issubclass(type(obj), BaseService):
                external_services.append(obj)
        return external_services

    @classmethod
    async def healthcheck(cls) -> bool:
        """Return whether every registered external service responds healthy."""

        for service in cls.get_external_services():
            try:
                is_ok = await service.ping()
                if not is_ok:
                    return False
            except Exception:
                return False
        return True

    @classmethod
    def healthcheck_router(cls):
        """Build a router exposing the aggregate service health check.

        Returns:
            A router with a ``/healthcheck`` endpoint.
        """
        router = APIRouter()

        @router.get(path="/healthcheck")
        async def healthcheck() -> JSONResponse:
            """Return the aggregate external-service health status."""

            is_ok = await cls.healthcheck()
            return JSONResponse(
                status_code=(200 if is_ok else 500),
                content={"status": "ok" if is_ok else "failed"},
            )

        return router

    @classmethod
    def docs_router(cls, service: Service | str = "", root_path: str = ""):
        """Build a router serving a locally hosted Swagger UI.

        Args:
            service: Optional service name displayed in the page title.
            root_path: Deployment root path prepended to documentation assets.

        Returns:
            A router with a custom ``/docs`` endpoint.
        """
        router = APIRouter()
        static_path = f"{root_path}/static/docs"

        @router.get(path="/docs", include_in_schema=False)
        async def docs() -> HTMLResponse:
            """Return the configured Swagger UI document."""

            return get_swagger_ui_html(
                openapi_url=f"{root_path}/openapi.json",
                title=f"{str(service).capitalize()} - Swagger UI" if service else "Swagger UI",
                oauth2_redirect_url=f"{root_path}/docs/oauth2-redirect",
                swagger_js_url=f"{static_path}/swagger-ui-bundle.js",
                swagger_css_url=f"{static_path}/swagger-ui.css",
                swagger_favicon_url=f"{static_path}/img/favicon.png",
            )

        return router

    @classmethod
    def configure_logging(cls):
        """Configure level and format of logging"""
        logging.basicConfig(level=cls.log_level, format=cls.logging_format)
