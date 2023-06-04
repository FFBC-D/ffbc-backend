from fastapi import FastAPI

from src.common.exceptions.handlers.fastapi_exception_handlers import (
    use_case_http_exception_handler,
)
from .api.router import include_endpoint_routers, include_admin_endpoint_routers
from .common.exceptions.base_exceptions import BaseHTTPException
from .containers import container


def create_app() -> FastAPI:
    application = FastAPI(debug=container.config.app.debug())
    application.container = container

    application.include_router(include_endpoint_routers(), prefix="/api")
    application.include_router(include_admin_endpoint_routers(), prefix="/api/admin")

    application.add_exception_handler(BaseHTTPException, use_case_http_exception_handler)

    return application


app = create_app()
