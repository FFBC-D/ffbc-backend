from src.common.admin.interfaces import IAdminUpdateUseCase
from src.common.exceptions.repository_exceptions import NotFoundException
from src.common.exceptions.use_case_exceptions import NotFoundHTTPException
from src.common.repository import ModelEntity, BaseRepo
from src.common.types.python_types import IdType, SchemaInType


class AdminUpdateUseCase(IAdminUpdateUseCase[IdType, SchemaInType, ModelEntity]):
    async def __call__(self, object_id: IdType, updated_object: SchemaInType) -> ModelEntity:
        async with self.uow:
            repository: BaseRepo = getattr(self.uow, self.repository_attr_name)
            try:
                entity = await repository.retrieve(self.filter_schema_class(id=object_id))
            except NotFoundException:
                raise NotFoundHTTPException

            for attr_name, attr_value in updated_object.dict(exclude_unset=True).items():
                setattr(entity, attr_name, attr_value)

            await self.uow.commit()
            await self.uow.refresh(entity)

        return entity
