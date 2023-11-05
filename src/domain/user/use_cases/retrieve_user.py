from dataclasses import dataclass

from src.data.database.models.user import User
from src.data.uow import UnitOfWork
from src.domain.user.dto.filter import UserFilterSchema


@dataclass
class RetrieveUser:
    uow: UnitOfWork

    async def __call__(self, data: UserFilterSchema) -> User:
        async with self.uow:
            return await self.uow.user.retrieve(data)
