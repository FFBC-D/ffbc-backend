import copy
from typing import Generic, Type, Sequence

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from src.common.dto import OrmModel
from src.common.exceptions.repository_exceptions import NotFoundException
from src.common.filters import FilterSet, Filter, InFilter, OrderingFilter, LimitOffsetPagination
from src.common.types.python_types import (
    FilterSchema,
    IdType,
    ModelEntity,
    SpecsSchema,
    FacetsSchema,
)


class AdminFilterSchema(OrmModel, Generic[IdType]):
    id: IdType | None
    ids: list[IdType] | None
    order: list[str] | None
    pagination: tuple[int, int] | None


class AdminFilterSet(FilterSet):
    id: Filter
    ids: InFilter
    order: OrderingFilter
    pagination: LimitOffsetPagination


class BaseRepo(Generic[ModelEntity, FilterSchema]):
    model: Type[ModelEntity]
    query: Select | None = None
    filter_set: Type[FilterSet] | None = None
    specs_schema: Type[SpecsSchema] | None = None
    facets_schema: Type[FacetsSchema] | None = None

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    def get_query(self) -> Select:
        query = self.query if self.query is not None else select(self.model)
        return copy.copy(query)

    async def filter(self, params: FilterSchema) -> Result:
        filter_set = self.filter_set(
            params.dict(exclude_unset=True), self.session, self.get_query()
        )
        filtered_query = filter_set.filter_query()
        return await self.session.execute(filtered_query)

    async def first(self, params: FilterSchema) -> ModelEntity:
        filtered_query = await self.filter(params)
        return filtered_query.scalars().first()

    async def retrieve(self, params: FilterSchema) -> ModelEntity:
        filtered_query = await self.filter(params)
        try:
            return filtered_query.scalars().one()
        except NoResultFound:
            raise NotFoundException

    def update(self, obj: ModelEntity, data: dict):
        for key, val in data.items():
            setattr(obj, key, val)

        self.session.add(obj)

    async def list(self, params: FilterSchema) -> Sequence[ModelEntity]:
        filtered_query = await self.filter(params)
        return filtered_query.scalars().all()

    def add(self, entity: ModelEntity) -> None:
        self.session.add(entity)

    async def delete(self, entity: ModelEntity) -> None:
        await self.session.delete(entity)

    async def add_all(self, *entities: ModelEntity) -> None:
        self.session.add_all([*entities])

    async def count(self, params: FilterSchema) -> int:
        query = self.get_query()
        filter_set = self.filter_set(params.dict(exclude_unset=True), self.session, query)
        return await filter_set.count()

    async def specs(self, params: FilterSchema, excluded_filters: None = None) -> SpecsSchema:
        query = self.get_query()
        filter_set = self.filter_set(params.dict(exclude_unset=True), self.session, query)
        specs = await filter_set.specs(excluded_filters=excluded_filters)
        return self.specs_schema(**specs)

    async def facets(self, params: FilterSchema, excluded_filters: None = None) -> FacetsSchema:
        query = self.get_query()
        filter_set = self.filter_set(params.dict(exclude_unset=True), self.session, query)
        facets = await filter_set.facets(excluded_filters=excluded_filters)
        return self.facets_schema(**facets)
