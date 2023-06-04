from typing import Any

from fastapi import HTTPException

from src.common.exceptions.error_codes import ErrorCode


class AppHTTPException(HTTPException):
    def __init__(
        self,
        error_code: ErrorCode,
        message: str | None,
        status_code: int | None = 400,
        **kwargs: dict[str, Any]
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail={"error_code": error_code, "message": message},
            **kwargs,
        )
