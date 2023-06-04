from dataclasses import dataclass

from src.data.database.models.jwt import BlacklistToken
from src.data.uow import UnitOfWork
from src.domain.jwt_token.dto.filter import OutstandingTokenFilterSchema


@dataclass
class AddJwtTokensToBlacklist:
    uow: UnitOfWork

    async def __call__(self, user_id: int) -> None:
        async with self.uow:
            outstanding_tokens = await self.uow.outstanding_token.list(
                OutstandingTokenFilterSchema(user_id=user_id, in_blacklist=False)
            )
            if not outstanding_tokens:
                return

            for outstanding_token in outstanding_tokens:
                blacklist_token = BlacklistToken(outstanding_token_id=outstanding_token.id)
                self.uow.blacklist_token.add(blacklist_token)

            await self.uow.commit()
