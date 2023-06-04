from src.common.admin.interfaces import IAdminRetrieveUseCase
from src.common.exceptions.repository_exceptions import NotFoundException
from src.common.exceptions.use_case_exceptions import NotFoundHTTPException
from src.common.repository import ModelEntity, BaseRepo
from src.common.types.python_types import IdType


class AdminRetrieveUseCase(IAdminRetrieveUseCase[IdType, ModelEntity]):
    async def __call__(self, object_id: IdType) -> ModelEntity:
        async with self.uow:
            repository: BaseRepo = getattr(self.uow, self.repository_attr_name)
            try:
                return await repository.retrieve(self.filter_schema_class(id=object_id))
            except NotFoundException:
                raise NotFoundHTTPException
