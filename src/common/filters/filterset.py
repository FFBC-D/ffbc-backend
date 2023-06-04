import abc
import copy
from collections import OrderedDict
from typing import Any, Callable, Mapping, Sequence

import sqlalchemy as sa
from sqlalchemy.engine import Result, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Bundle
from sqlalchemy.sql import ColumnElement, Select

from src.common.filters.filters import BaseFilter, OrderingFilter
from src.common.filters.interfaces import IFilterSet
from src.common.utils.concurrency import gather_with_concurrency

CHUNK_SIZE = 100


class FilterSetMetaclass(type):
    """Метакласс для создания FilterSet"""

    def __new__(mcs, name: str, bases: tuple, attrs: dict) -> "FilterSetMetaclass":
        attrs["declared_filters"] = mcs.get_declared_filters(attrs)
        new_class = super().__new__(mcs, name, bases, attrs)
        new_class.base_filters = new_class.get_filters()

        return new_class

    @classmethod
    def get_declared_filters(mcs, attrs: dict) -> OrderedDict:
        filters = [
            (filter_name, attrs.pop(filter_name))
            for filter_name, obj in list(attrs.items())
            if isinstance(obj, BaseFilter)
        ]

        for filter_name, f in filters:
            if getattr(f, "field_name", None) is None:
                f.field_name = filter_name

        return OrderedDict(filters)


class BaseFilterSet(IFilterSet):
    """Базовый FilterSet"""

    declared_filters: OrderedDict

    def __init__(
        self,
        params: dict,
        session: AsyncSession,
        query: Select,
        enable_optimization: bool = True,
    ) -> None:
        """
        :param params: Словарь параметров для фильтрации
        :param session: Сессия базы данных
        :param query: Базовый запрос, на основе которого происходит фильтрация
        :param enable_optimization: Включает оптимизацию запросов при вычислении specs и facets
        """
        self.params = params
        self.__base_query = query
        self.session = session
        # self.base_filters = self.get_filters()
        self.filters = copy.deepcopy(self.base_filters)
        self._optimization_enabled = enable_optimization
        for filter_ in self.filters.values():
            filter_.parent = self

    def get_base_query(self) -> Select:
        return copy.copy(self.__base_query)

    @property
    def optimization_enabled(self) -> bool:
        # Оптимизация не совместима с DISTINCT и DISTINCT ON
        if self.get_base_query()._distinct:  # type: ignore
            return False
        return self._optimization_enabled

    @staticmethod
    def check_undefined_fields(filters: Any) -> None:
        undefined = []

        for filter_ in filters:
            if isinstance(filter_, OrderingFilter):
                for model, field in filter_.fields.values():
                    if model and not hasattr(model, field):
                        undefined.append(field)

            if not hasattr(filter_, "model"):
                continue

            model = filter_.model

            if hasattr(filter_, "field") and not hasattr(model, filter_.field):
                undefined.append(filter_.field)

            if hasattr(filter_, "fields"):
                if isinstance(filter_, OrderingFilter):
                    continue
                else:
                    for field in filter_.fields:
                        if not hasattr(model, field):
                            undefined.append(field)

        if undefined:
            raise TypeError(
                f"FilterSet must not contain non-model field names: {', '.join(undefined)}"
            )

    @classmethod
    def get_filters(cls) -> OrderedDict[str, BaseFilter]:
        """Получение фильтров для данного FilterSet"""
        filters: OrderedDict = OrderedDict()
        cls.check_undefined_fields(cls.declared_filters.values())
        filters.update(cls.declared_filters)
        return filters

    def filter_query(self) -> Select:
        """Построение запроса для фильтрации"""
        query = self.get_base_query()
        for name, value in self.params.items():
            if name not in self.filters:
                continue
            query = self.filters[name].filter(query, value)
        return query

    async def filter(self) -> Result:
        return await self.session.execute(self.filter_query())

    async def specs(self, excluded_filters: list[str] | None = None) -> dict[str, Any]:
        """Получения specs для данного FilterSet"""
        tasks: list = []
        fields: list = []
        query = self.filter_query()
        if self.optimization_enabled:
            tasks.append(self._get_specs_common_columns(excluded_filters))
            query = query.order_by(None)

        for filter_name, _filter in self.filters.items():
            if excluded_filters is not None and filter_name in excluded_filters:
                continue
            if (
                self.optimization_enabled
                and _filter.has_specs_columns
                and filter_name not in self.params
            ):
                continue
            if _filter.has_specs:
                tasks.append(_filter.specs(self.session, query))
                fields.append(filter_name)

        tasks_result = await gather_with_concurrency(CHUNK_SIZE, *tasks)
        result = tasks_result.pop(0) if self.optimization_enabled else {}
        result.update(dict(zip(fields, tasks_result)))
        return result

    async def facets(self, excluded_filters: list[str] | None = None) -> dict[str, Any]:
        """Получения фасетов для данного FilterSet"""
        tasks: list = []
        fields: list = []

        if self.optimization_enabled:
            tasks.append(self._get_facets_common_columns(excluded_filters))

        for filter_name, _filter in self.filters.items():
            if excluded_filters is not None and filter_name in excluded_filters:
                continue
            if (
                self.optimization_enabled
                and _filter.has_facets_columns
                and filter_name not in self.params
            ):
                continue
            if _filter.has_facets:
                backup_filters = self.params.copy()
                self.params.pop(filter_name, None)
                query = self.filter_query()
                if self.optimization_enabled:
                    query = query.order_by(None)

                tasks.append(_filter.facets(self.session, query))
                fields.append(filter_name)

                self.params = backup_filters

        tasks_result = await gather_with_concurrency(CHUNK_SIZE, *tasks)
        result = tasks_result.pop(0) if self.optimization_enabled else {}
        result.update(dict(zip(fields, tasks_result)))
        return result

    async def count(
        self, attr_name: str = "id", distinct: bool = False, exclude_pagination: bool = True
    ) -> int:
        """Получения кол-ва результатов для данного FilterSet"""
        base_query = self.filter_query().order_by(None)
        if exclude_pagination:
            base_query = base_query.limit(None).offset(None)
        subquery = base_query.alias("s")
        attr = getattr(subquery.c, attr_name)
        if distinct:
            attr = sa.distinct(attr)
        query = sa.select([sa.func.count(attr)])
        return (await self.session.execute(query)).scalar()  # type: ignore

    async def _get_specs_common_columns(
        self, excluded_filters: list[str] | None = None
    ) -> dict[str, Any]:
        """Получения specs в общем запросе для данного FilterSet"""
        query_columns: list[Bundle | ColumnElement] = list()
        field_name_to_parser: OrderedDict[str, Callable] = OrderedDict()

        for filter_name, _filter in self.filters.items():
            if excluded_filters is not None and filter_name in excluded_filters:
                continue
            if _filter.has_specs_columns and filter_name not in self.params.keys():
                columns, parse = _filter.specs_columns()
                query_columns.append(columns)
                field_name_to_parser.update({filter_name: parse})

        if not field_name_to_parser:
            return {}

        results = await self._fetch_common_columns(query_columns)
        return self._parse_common_columns(results, field_name_to_parser)

    async def _get_facets_common_columns(
        self, excluded_filters: list[str] | None = None
    ) -> dict[str, Any]:
        """Получения facets в общем запросе для данного FilterSet"""
        query_columns: list[Bundle | ColumnElement] = [sa.func.count().label("count")]
        field_name_to_parser: OrderedDict[str, Callable] = OrderedDict({"count": lambda val: val})

        for filter_name, _filter in self.filters.items():
            if excluded_filters is not None and filter_name in excluded_filters:
                continue
            if _filter.has_facets_columns and filter_name not in self.params.keys():
                columns, parse = _filter.facets_columns()
                query_columns.append(columns)
                field_name_to_parser.update({filter_name: parse})

        results = await self._fetch_common_columns(query_columns)
        return self._parse_common_columns(results, field_name_to_parser)

    async def _fetch_common_columns(self, columns: Sequence[Bundle | ColumnElement]) -> Row:
        query = self.filter_query()
        query = query.with_only_columns(columns).order_by(None)
        return (await self.session.execute(query)).one()

    @staticmethod
    def _parse_common_columns(
        result: Row, field_name_to_parser: Mapping[str, Callable]
    ) -> dict[str, Any]:
        mapped_result: dict[str, Any] = {}
        for field_name, parse in field_name_to_parser.items():
            mapped_result[field_name] = parse(getattr(result, field_name))
        return mapped_result


class ABCFilterSetMetaclass(abc.ABCMeta, FilterSetMetaclass):
    pass


class FilterSet(BaseFilterSet, metaclass=ABCFilterSetMetaclass):
    pass
