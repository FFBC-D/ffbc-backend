from sqlalchemy.exc import IntegrityError

from src.common.admin.interfaces import IAdminCreateUseCase
from src.common.exceptions.handlers.exception_handlers import handle_integrity_exception
from src.common.exceptions.use_case_exceptions import UseCaseHTTPException
from src.common.repository import BaseRepo
from src.data.database.models.user import User
from src.domain.user.dto.admin import UserAdminCreateSchema
from src.utils.security import get_password_hash


class CreateUserAdmin(IAdminCreateUseCase[UserAdminCreateSchema, User]):
    async def __call__(self, new_object: UserAdminCreateSchema) -> User:
        async with self.uow:
            repository: BaseRepo = getattr(self.uow, self.repository_attr_name)
            user_data = {
                **new_object.dict(exclude_unset=True, exclude={"password", "password_repeat"}),
                "hashed_password": get_password_hash(new_object.password),
            }
            user = User(**user_data)
            repository.add(user)

            try:
                await self.uow.commit()
            except IntegrityError as e:
                result = handle_integrity_exception(e)
                raise UseCaseHTTPException(**result._asdict())

            await self.uow.refresh(user)
            return user
