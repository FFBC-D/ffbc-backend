from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.use_case_exceptions import UseCaseHTTPException
from src.data.database.models.user import User
from src.data.uow import UnitOfWork
from src.domain.user.dto.filter import UserFilterSchema
from src.domain.user.dto.input import AuthInSchema
from src.utils.security import verify_password


class Authenticate:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def __call__(self, data: AuthInSchema) -> User:
        async with self.uow:
            user_db = await self.uow.user.first(params=UserFilterSchema(email=data.email))
            if not user_db or not verify_password(data.password, user_db.hashed_password):
                raise UseCaseHTTPException(message="User not found", error_code=ErrorCode.NOT_FOUND)
            return user_db
