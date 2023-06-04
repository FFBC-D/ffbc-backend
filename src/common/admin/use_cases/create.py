from sqlalchemy.exc import IntegrityError

from src.common.admin.interfaces import IAdminCreateUseCase
from src.common.exceptions.handlers.exception_handlers import handle_integrity_exception
from src.common.exceptions.use_case_exceptions import UseCaseHTTPException
from src.common.repository import BaseRepo, ModelEntity
from src.common.types.python_types import SchemaInType


class AdminCreateUseCase(IAdminCreateUseCase[SchemaInType, ModelEntity]):
    async def __call__(self, new_object: SchemaInType) -> ModelEntity:
        async with self.uow:
            repository: BaseRepo = getattr(self.uow, self.repository_attr_name)
            entity = self.entity_class(**new_object.dict(exclude_unset=True))

            repository.add(entity)

            try:
                await self.uow.commit()
            except IntegrityError as e:
                result = handle_integrity_exception(e)
                raise UseCaseHTTPException(**result._asdict())

        return entity
