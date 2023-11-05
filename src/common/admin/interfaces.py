import abc
from dataclasses import dataclass
from typing import Generic, Type, ClassVar

from src.common.repository import ModelEntity
from src.common.types.python_types import (
    IdType,
    AdminFilterSchema,
    SchemaInType,
    SpecsSchema,
    FacetsSchema,
)
from src.common.uow import BaseUnitOfWork


@dataclass
class IAdminCreateUseCase(Generic[SchemaInType, ModelEntity], abc.ABC):
    uow: BaseUnitOfWork
    repository_attr_name: str
    entity_class: Type[ModelEntity]

    @abc.abstractmethod
    async def __call__(self, new_object: SchemaInType) -> ModelEntity:
        ...


@dataclass
class IAdminListUseCase(
    Generic[AdminFilterSchema, ModelEntity, SpecsSchema, FacetsSchema],
    abc.ABC,
):
    uow: BaseUnitOfWork
    repository_attr_name: str

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


@dataclass
class IAdminRetrieveUseCase(Generic[IdType, ModelEntity], abc.ABC):
    uow: BaseUnitOfWork
    repository_attr_name: str
    filter_schema_class: Type[AdminFilterSchema]

    @abc.abstractmethod
    async def __call__(self, object_id: IdType) -> ModelEntity:
        ...


@dataclass
class IAdminUpdateUseCase(Generic[IdType, SchemaInType, ModelEntity], abc.ABC):
    uow: BaseUnitOfWork
    repository_attr_name: str
    filter_schema_class: Type[AdminFilterSchema]

    @abc.abstractmethod
    async def __call__(self, object_id: IdType, updated_object: SchemaInType) -> ModelEntity:
        ...


@dataclass
class IAdminDeleteUseCase(Generic[IdType], abc.ABC):
    uow: BaseUnitOfWork
    repository_attr_name: str
    filter_schema_class: Type[AdminFilterSchema]

    @abc.abstractmethod
    async def __call__(self, object_id: IdType) -> None:
        ...


@dataclass
class IAdminUpdateFilesUseCase(Generic[IdType, SchemaInType, ModelEntity], abc.ABC):
    uow: BaseUnitOfWork
    repository_attr_name: str
    filter_schema_class: Type[AdminFilterSchema]

    @abc.abstractmethod
    async def __call__(self, object_id: IdType, data: SchemaInType) -> ModelEntity:
        ...


@dataclass
class IAdminLinkM2mObjectUseCase(abc.ABC):
    uow: BaseUnitOfWork
    main_model_repository_attr_name: ClassVar[str]
    link_model_repository_attr_name: ClassVar[str]
    link_model_field_name: ClassVar[str]

    @abc.abstractmethod
    async def __call__(self, main_model_id: int, link_model_id: int) -> None:
        ...
