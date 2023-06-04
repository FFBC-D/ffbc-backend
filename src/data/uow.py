from src.common.uow import BaseUnitOfWork
from src.data.admin_repositories.user import UserAdminRepo
from src.data.repositories.blacklist_token import BlacklistTokenRepo
from src.data.repositories.outstanding_token import OutstandingTokenRepo
from src.data.repositories.user import UserRepo


class UnitOfWork(BaseUnitOfWork):
    async def __aenter__(self) -> None:
        await super().__aenter__()

        self.user = UserRepo(session=self.session)
        self.outstanding_token = OutstandingTokenRepo(session=self.session)
        self.blacklist_token = BlacklistTokenRepo(session=self.session)

        # Admin repos
        self.user_admin = UserAdminRepo(session=self.session)
