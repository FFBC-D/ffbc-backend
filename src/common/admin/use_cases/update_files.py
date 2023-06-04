from src.common.admin.interfaces import IAdminUpdateFilesUseCase
from src.common.exceptions.repository_exceptions import NotFoundException
from src.common.exceptions.use_case_exceptions import NotFoundHTTPException
from src.common.repository import BaseRepo
from src.common.types.python_types import IdType, SchemaInType, ModelEntity


class AdminUpdateFilesUseCase(IAdminUpdateFilesUseCase[IdType, SchemaInType, ModelEntity]):
    async def __call__(self, object_id: IdType, data: SchemaInType) -> ModelEntity:
        async with self.uow:
            repository: BaseRepo = getattr(self.uow, self.repository_attr_name)
            try:
                entity = await repository.retrieve(self.filter_schema_class(id=object_id))
            except NotFoundException:
                raise NotFoundHTTPException

            for attr_name, attr_value in data.dict(exclude_unset=True).items():
                setattr(entity, attr_name, attr_value)

            await self.uow.commit()

        return entity
