from src.common.admin.interfaces import IAdminDeleteUseCase
from src.common.exceptions.repository_exceptions import NotFoundException
from src.common.exceptions.use_case_exceptions import NotFoundHTTPException
from src.common.repository import BaseRepo
from src.common.types.python_types import IdType


class AdminDeleteUseCase(IAdminDeleteUseCase[IdType]):
    async def __call__(self, object_id: IdType) -> None:
        async with self.uow:
            repository: BaseRepo = getattr(self.uow, self.repository_attr_name)
            try:
                entity = await repository.retrieve(self.filter_schema_class(id=object_id))
            except NotFoundException:
                raise NotFoundHTTPException

            await repository.delete(entity)
            await self.uow.commit()
