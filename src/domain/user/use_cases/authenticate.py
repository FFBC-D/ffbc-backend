from fastapi import HTTPException

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
                raise HTTPException(status_code=400, detail="User not found")
            return user_db
