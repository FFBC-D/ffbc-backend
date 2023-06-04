from typing import Annotated

from fastapi import Depends

from src.common.dependencies.current_user import get_current_user
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.http_exceptions import AppHTTPException
from src.data.database.models.user import User


async def get_current_authenticated_user(user: User | None = Depends(get_current_user)) -> User:
    if user is None:
        raise AppHTTPException(
            status_code=401,
            error_code=ErrorCode.AUTH_ERROR,
            message="User not found",
        )
    return user


CurrentAuthenticatedUser = Annotated[User, Depends(get_current_authenticated_user)]
