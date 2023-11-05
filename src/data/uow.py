from src.common.uow import BaseUnitOfWork
from src.data.admin_repositories.products.measure_category import MeasureCategoryAdminRepo
from src.data.admin_repositories.products.measure_value import MeasureValueAdminRepo
from src.data.admin_repositories.products.product import ProductAdminRepo
from src.data.admin_repositories.products.product_category import ProductCategoryAdminRepo
from src.data.admin_repositories.products.product_modification import ProductModificationAdminRepo
from src.data.admin_repositories.products.product_modification_value import ProductModificationValueAdminRepo
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
        self.measure_category_admin = MeasureCategoryAdminRepo(session=self.session)
        self.measure_value_admin = MeasureValueAdminRepo(session=self.session)
        self.product_admin = ProductAdminRepo(session=self.session)
        self.product_category_admin = ProductCategoryAdminRepo(session=self.session)
        self.product_modification_admin = ProductModificationAdminRepo(session=self.session)
        self.product_modification_value_admin = ProductModificationValueAdminRepo(
            session=self.session
        )
