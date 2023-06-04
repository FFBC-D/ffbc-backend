from types import TracebackType
from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession

from src.common.repository import ModelEntity


class BaseUnitOfWork:
    def __init__(self, scoped_session: AsyncSession):
        self.scoped_session = scoped_session

    async def __aenter__(self) -> None:
        self.session: AsyncSession = self.scoped_session

    async def __aexit__(
        self,
        exc_t: Type[BaseException] | None,
        exc_v: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def refresh(self, obj: ModelEntity) -> None:
        await self.session.refresh(obj)
