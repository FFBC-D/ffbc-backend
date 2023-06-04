from src.common.exceptions.base_exceptions import BaseHTTPException
from src.common.exceptions.error_codes import ErrorCode


class UseCaseHTTPException(BaseHTTPException):
    status: int = 400

    def __init__(self, message: str, error_code: ErrorCode, field: str | None = "non_field"):
        self.message = message
        self.error_code = error_code
        self.field = field


class NotFoundHTTPException(BaseHTTPException):
    status: int = 404
    error_code = ErrorCode.NOT_FOUND
    field: str = "non_field"
    message: str = "Object does not exist"

    def __init__(self, message: str | None = None):
        if message:
            self.message = message
