from src.data.database.models.user import User
from src.data.uow import UnitOfWork
from src.domain.user.dto.filter import UserFilterSchema


class RetrieveUser:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def __call__(self, data: UserFilterSchema) -> User:
        async with self.uow:
            return await self.uow.user.retrieve(data)
