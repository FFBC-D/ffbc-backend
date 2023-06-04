from src.common.exceptions.error_codes import ErrorCode


class BaseException(Exception):
    message: str


class BaseHTTPException(Exception):
    message: str
    status: int
    error_code: ErrorCode
    field: str
