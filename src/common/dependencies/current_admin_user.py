from typing import Annotated

from fastapi import Depends

from src.common.dependencies.current_authenticated_user import get_current_authenticated_user
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.http_exceptions import AppHTTPException
from src.data.database.models.user import User


async def get_current_admin_user(user: User = Depends(get_current_authenticated_user)) -> User:
    if not user.is_admin:
        raise AppHTTPException(
            status_code=403,
            error_code=ErrorCode.AUTH_ERROR,
            message="User is not admin",
        )
    return user


CurrentAdminUser = Annotated[User, Depends(get_current_admin_user)]
