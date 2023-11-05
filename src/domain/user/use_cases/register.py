from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from src.common.exceptions.handlers.exception_handlers import handle_integrity_exception
from src.common.exceptions.use_case_exceptions import UseCaseHTTPException
from src.data.database.models.user import User
from src.data.uow import UnitOfWork
from src.domain.user.dto.input import RegisterInSchema
from src.utils.security import get_password_hash


@dataclass
class Register:
    uow: UnitOfWork

    async def __call__(self, data: RegisterInSchema) -> None:
        async with self.uow:
            obj = User(
                email=data.email,
                first_name=data.first_name,
                last_name=data.last_name,
                hashed_password=get_password_hash(data.password),
            )

            self.uow.user.add(obj)
            try:
                await self.uow.commit()
            except IntegrityError as e:
                result = handle_integrity_exception(e)
                raise UseCaseHTTPException(**result._asdict())
