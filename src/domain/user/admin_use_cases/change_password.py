from dataclasses import dataclass

from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.repository_exceptions import NotFoundException
from src.common.exceptions.use_case_exceptions import UseCaseHTTPException
from src.data.uow import UnitOfWork
from src.domain.user.dto.admin import (
    UserAdminFilterSchema,
    UserAdminUpdatePasswordSchema,
)
from src.utils.security import get_password_hash


@dataclass
class ChangePasswordAdmin:
    uow: UnitOfWork

    async def __call__(self, pk: int, data: UserAdminUpdatePasswordSchema) -> None:
        async with self.uow:
            try:
                user = await self.uow.user_admin.retrieve(UserAdminFilterSchema(id=pk))
            except NotFoundException:
                raise UseCaseHTTPException(
                    error_code=ErrorCode.NOT_FOUND,
                    message="User not found",
                )

            user.hashed_password = get_password_hash(data.password)
            self.uow.user_admin.add(user)
            await self.uow.commit()
