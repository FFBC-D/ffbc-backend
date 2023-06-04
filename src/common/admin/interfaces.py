import abc
from typing import Generic, Type

from src.common.repository import ModelEntity
from src.common.types.python_types import (
    IdType,
    AdminFilterSchema,
    SchemaInType,
    SpecsSchema,
    FacetsSchema,
)
from src.common.uow import BaseUnitOfWork


class IAdminCreateUseCase(Generic[SchemaInType, ModelEntity], abc.ABC):
    def __init__(
        self,
        uow: BaseUnitOfWork,
        repository_attr_name: str,
        entity_class: Type[ModelEntity],
    ) -> None:
        self.uow = uow
        self.repository_attr_name = repository_attr_name
        self.entity_class = entity_class

    @abc.abstractmethod
    async def __call__(self, new_object: SchemaInType) -> ModelEntity:
        ...


class IAdminListUseCase(
    Generic[AdminFilterSchema, ModelEntity, SpecsSchema, FacetsSchema],
    abc.ABC,
):
    def __init__(self, uow: BaseUnitOfWork, repository_attr_name: str) -> None:
        self.uow = uow
        self.repository_attr_name = repository_attr_name

    @abc.abstractmethod
    async def __call__(self, filter_schema: AdminFilterSchema) -> list[ModelEntity]:
        ...

    @abc.abstractmethod
    async def count(self, filter_schema: AdminFilterSchema) -> int:
        ...

    @abc.abstractmethod
    async def specs(self, filter_schema: AdminFilterSchema) -> SpecsSchema:
        ...

    @abc.abstractmethod
    async def facets(self, filter_schema: AdminFilterSchema) -> FacetsSchema:
        ...


class IAdminRetrieveUseCase(Generic[IdType, ModelEntity], abc.ABC):
    def __init__(
        self,
        uow: BaseUnitOfWork,
        repository_attr_name: str,
        filter_schema_class: Type[AdminFilterSchema],
    ) -> None:
        self.uow = uow
        self.repository_attr_name = repository_attr_name
        self.filter_schema_class = filter_schema_class

    @abc.abstractmethod
    async def __call__(self, object_id: IdType) -> ModelEntity:
        ...


class IAdminUpdateUseCase(Generic[IdType, SchemaInType, ModelEntity], abc.ABC):
    def __init__(
        self,
        uow: BaseUnitOfWork,
        repository_attr_name: str,
        filter_schema_class: Type[AdminFilterSchema],
    ) -> None:
        self.uow = uow
        self.repository_attr_name = repository_attr_name
        self.filter_schema_class = filter_schema_class

    @abc.abstractmethod
    async def __call__(self, object_id: IdType, updated_object: SchemaInType) -> ModelEntity:
        ...


class IAdminDeleteUseCase(Generic[IdType], abc.ABC):
    def __init__(
        self,
        uow: BaseUnitOfWork,
        repository_attr_name: str,
        filter_schema_class: Type[AdminFilterSchema],
    ) -> None:
        self.uow = uow
        self.repository_attr_name = repository_attr_name
        self.filter_schema_class = filter_schema_class

    @abc.abstractmethod
    async def __call__(self, object_id: IdType) -> None:
        ...


class IAdminUpdateFilesUseCase(Generic[IdType, SchemaInType, ModelEntity], abc.ABC):
    def __init__(
        self,
        uow: BaseUnitOfWork,
        repository_attr_name: str,
        filter_schema_class: Type[AdminFilterSchema],
    ) -> None:
        self.uow = uow
        self.repository_attr_name = repository_attr_name
        self.filter_schema_class = filter_schema_class

    @abc.abstractmethod
    async def __call__(self, object_id: IdType, data: SchemaInType) -> ModelEntity:
        ...
