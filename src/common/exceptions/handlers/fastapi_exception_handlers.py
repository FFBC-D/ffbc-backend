from starlette.requests import Request
from starlette.responses import JSONResponse

from src.common.exceptions.base_exceptions import BaseHTTPException


def use_case_http_exception_handler(request: Request, exc: BaseHTTPException):
    return JSONResponse(
        status_code=exc.status,
        content={"message": exc.message, "error_code": exc.error_code, "field": exc.field},
    )
