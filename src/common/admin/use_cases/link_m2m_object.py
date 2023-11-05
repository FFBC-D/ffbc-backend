from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.common.admin.interfaces import IAdminLinkM2mObjectUseCase
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.handlers.exception_handlers import handle_integrity_exception
from src.common.exceptions.repository_exceptions import NotFoundException
from src.common.exceptions.use_case_exceptions import NotFoundHTTPException
from src.common.exceptions.use_case_exceptions import UseCaseHTTPException
from src.common.repository import BaseRepo


class BaseFilterSchema(BaseModel):
    id: int | str | UUID


class AdminLinkM2mObjectUseCase(IAdminLinkM2mObjectUseCase):
    async def __call__(
        self, main_model_id: int, link_model_id: int, unlink: Optional[bool] = False
    ) -> None:
        async with self.uow:
            main_model_repository: BaseRepo = getattr(
                self.uow, self.main_model_repository_attr_name
            )
            link_model_repository: BaseRepo = getattr(
                self.uow, self.link_model_repository_attr_name
            )

            main_model = await self.retrieve_obj(main_model_repository, main_model_id)
            link_model = await self.retrieve_obj(link_model_repository, link_model_id)

            m2m_model = getattr(main_model, self.link_model_field_name)
            if not unlink:
                m2m_model.append(link_model)
            else:
                try:
                    m2m_model.remove(link_model)
                except ValueError:
                    raise UseCaseHTTPException(
                        message="Instance is not linked",
                        error_code=ErrorCode.INSTANCE_ALREADY_UNLINKED,
                        field="non_field",
                    )

            main_model_repository.add(main_model)

            try:
                await self.uow.commit()
            except IntegrityError as e:
                result = handle_integrity_exception(e)
                raise UseCaseHTTPException(**result._asdict())

    async def retrieve_obj(self, repository: BaseRepo, obj_id: int | str | UUID):
        try:
            return await repository.retrieve(BaseFilterSchema(id=obj_id))
        except NotFoundException:
            raise NotFoundHTTPException
