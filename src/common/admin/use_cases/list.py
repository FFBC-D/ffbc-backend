from src.common.admin.interfaces import IAdminListUseCase
from src.common.repository import ModelEntity, SpecsSchema, FacetsSchema, BaseRepo
from src.common.types.python_types import AdminFilterSchema


class AdminListUseCase(
    IAdminListUseCase[AdminFilterSchema, ModelEntity, SpecsSchema, FacetsSchema],
):
    async def __call__(self, filter_schema: AdminFilterSchema) -> list[ModelEntity]:
        async with self.uow:
            repository: BaseRepo = getattr(self.uow, self.repository_attr_name)
            results = await repository.list(filter_schema)
        return results  # type: ignore

    async def count(self, filter_schema: AdminFilterSchema) -> int:
        async with self.uow:
            repository: BaseRepo = getattr(self.uow, self.repository_attr_name)
            return await repository.count(filter_schema)

    async def specs(self, filter_schema: AdminFilterSchema) -> SpecsSchema:
        async with self.uow:
            repository: BaseRepo = getattr(self.uow, self.repository_attr_name)
            return await repository.specs(filter_schema)

    async def facets(self, filter_schema: AdminFilterSchema) -> FacetsSchema:
        async with self.uow:
            repository: BaseRepo = getattr(self.uow, self.repository_attr_name)
            return await repository.facets(filter_schema)
