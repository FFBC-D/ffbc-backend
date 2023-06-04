from fastapi import status

from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.http_exceptions import AppHTTPException


def get_token_from_bearer_string(bearer_string: str) -> str:
    try:
        return bearer_string.split(" ")[1]
    except IndexError:
        raise AppHTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=ErrorCode.AUTH_ERROR,
            message="Invalid Bearer string",
        )
