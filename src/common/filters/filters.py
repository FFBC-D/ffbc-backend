import abc
import operator as operators
from typing import TYPE_CHECKING, Any, Callable, Optional, Sequence, Type

import sqlalchemy as sa
from pydantic import BaseModel, parse_obj_as
from sqlalchemy import cast, func
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Bundle
from sqlalchemy.sql import ColumnElement, Select

from src.common.database.mixins import BaseClass
from src.common.enums import ChoicesEnum
from src.common.filters.constants import EMPTY_VALUES
from src.common.filters.interfaces import IBaseFilter
from src.common.filters.schemas import ChoiceSchema, NumberFilterSpecsSchema

if TYPE_CHECKING:
    from src.common.filters.interfaces import IFilterSet


class BaseFilter(IBaseFilter):
    """Абстрактный класс фильтра"""

    field_name: str | None = None
    "Название фильтра в filterset. проставляется в метаклассе при создании."
    has_specs: bool = False
    "Показатель того, что фильтр имплементировал метод получения specs"
    has_facets: bool = False
    "Показатель того, что фильтр имплементировал метод получения facets"
    has_specs_columns: bool = False
    "Показатель того, что фильтр имплементировал метод получения specs в колонке основного запроса"
    has_facets_columns: bool = False
    "Показатель того, что фильтр имплементировал метод получения facets в колонке основного запроса"

    @abc.abstractmethod
    def filter(self, query: Select, value: Any) -> Select:
        """Метод реализующий фильтрацию"""
        ...

    async def specs(self, session: AsyncSession, query: Select) -> bool | list | dict | None:
        """Метод реализующий получение specs"""
        raise NotImplementedError

    async def facets(self, session: AsyncSession, query: Select) -> bool | list | dict | None:
        """Метод реализующий получение facets"""
        raise NotImplementedError

    def specs_columns(self) -> tuple[Bundle | ColumnElement, Callable]:
        """Метод реализующий получение specs в колонке общего запроса"""
        raise NotImplementedError

    def facets_columns(self) -> tuple[Bundle | ColumnElement, Callable]:
        """Метод реализующий получение facets в колонке общего запроса"""
        raise NotImplementedError


class Filter(BaseFilter):
    """Базовый фильтр для поля модели"""

    def __init__(
        self,
        model: Type[BaseClass],
        field: str,
        *,
        exclude: bool = False,
        nullable: bool = False,
    ) -> None:
        """
        :param model: Модель для фильтрации
        :param field: Поле модели для фильтрации
        :param exclude: Производить инвертированную фильтрацию
        :param nullable: Допускать пустые значения
        """
        super().__init__()
        self.model = model
        self.field = field
        self.exclude = exclude
        self.nullable = nullable

    def filter(self, query: Select, value: Any) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query

        expression = getattr(self.model, self.field) == value
        return query.where(~expression if self.exclude else expression)


class InFilter(Filter):
    def filter(self, query: Select, value: Sequence) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query

        expression = getattr(self.model, self.field).in_(value)
        return query.where(~expression if self.exclude else expression)


class CharFilter(Filter):
    """Фильтр по строке"""

    has_specs: bool = True
    has_facets: bool = True
    has_specs_columns: bool = False
    has_facets_columns: bool = True

    def __init__(
        self,
        model: Type[BaseClass],
        field: str,
        *,
        specs_schema: Type[Sequence[BaseModel]] = list[ChoiceSchema],
        display_attr: str | None = None,
        order_by_attr: str | None = None,
        enum_type: Type[ChoicesEnum] | None = None,
        exclude: bool = False,
        nullable: bool = False,
    ) -> None:
        """
        :param model: Модель для фильтрации
        :param field: Поле модели для фильтрации
        :param specs_schema: Сериализатор спеков
        :param display_attr: атрибут для отображения в спеках.
        Пример: field = "id", display_attr = "title" в результате дадут
        {"id": "some id", "title": "some title"}
        :param order_by_attr: Атрибут, по которому произведётся сортировка спеков
        :param enum_type: Отображать название из Enum
        :param exclude: Производить инвертированную фильтрацию
        :param nullable: Допускать пустые значения
        """
        super().__init__(model=model, field=field, exclude=exclude, nullable=nullable)
        self.specs_schema = specs_schema
        self.display_attr = display_attr
        self.order_by_attr = order_by_attr
        self.enum_type = enum_type

    def facets_columns(self) -> tuple[Bundle | ColumnElement, Callable]:
        if not any([self.display_attr, self.enum_type]):
            return sa.select(sa.text("1")).label(self.field_name), lambda x: None

        field = sa.cast(getattr(self.model, self.field), sa.String)
        bundle = (
            func.array_agg(aggregate_order_by(sa.distinct(field), field.asc()))
            .filter(field.is_not(None))
            .label(self.field_name)
        )

        def parse(result: Any) -> list:
            return result if result else []

        return bundle, parse

    async def specs(self, session: AsyncSession, query: Select) -> list[dict] | None:
        value_field: ColumnElement
        if self.display_attr:
            order_by_attr: str = self.order_by_attr or self.field
            reverse_ordering: bool = order_by_attr.startswith("-")
            sort_func = sa.desc if reverse_ordering else sa.asc
            order_by_attr = order_by_attr[1:] if reverse_ordering else order_by_attr

            subquery = query.add_columns(
                getattr(self.model, self.field).label("value"),
                getattr(self.model, self.display_attr).label("label"),
                getattr(self.model, order_by_attr).label("order_by"),
            ).subquery("c")
            value_field = sa.distinct(sa.cast(subquery.c.value, sa.String)).label("value")
            label_field = sa.cast(subquery.c.label, sa.String).label("label")
            order_by_field = sa.cast(subquery.c.order_by, sa.String).label("order_by")
            choices_query = (
                sa.select(value_field, label_field, order_by_field)
                .where(subquery.c.value.isnot(None))
                .order_by(sort_func(order_by_field))
            )
            choices = (await session.execute(choices_query)).all()
            specs: Sequence[BaseModel] = parse_obj_as(self.specs_schema, choices)
            return [i.dict() for i in specs if i.dict().get("label")]
        elif self.enum_type:
            subquery = query.add_columns(
                getattr(self.model, self.field).label("value"),
            ).subquery("c")
            value_field = sa.distinct(sa.cast(subquery.c.value, sa.String)).label("value")
            choices_query = (
                sa.select(value_field).where(subquery.c.value.isnot(None)).order_by(value_field)
            )
            choices = (await session.execute(choices_query)).unique().scalars().all()
            return [
                {"value": choice.value, "label": choice.display}
                for choice in self.enum_type  # type: ignore
                if choice.value in choices
            ]
        return None

    async def facets(self, session: AsyncSession, query: Select) -> list | None:
        if not any([self.display_attr, self.enum_type]):
            return None

        field = sa.cast(getattr(self.model, self.field).label("value"), sa.String)
        query = (
            query.with_only_columns(field)
            .where(field.is_not(None))
            .order_by(field.asc())
            .distinct()
        )
        return (await session.execute(query)).unique().scalars().all()


class CharInFilter(CharFilter):
    """Фильтр по вхождению строки в список"""

    def filter(self, query: Select, value: Sequence) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query

        expression = getattr(self.model, self.field).in_(value)
        return query.where(~expression if self.exclude else expression)


class EnumFilter(Filter):
    """Фильтр по ChoicesEnum"""

    has_specs: bool = True
    has_facets: bool = True
    has_specs_columns: bool = True
    has_facets_columns: bool = True

    def specs_columns(self) -> tuple[Bundle | ColumnElement, Callable]:
        field = getattr(self.model, self.field)
        bundle = (
            func.array_agg(aggregate_order_by(sa.distinct(field), field.asc()))
            .filter(field.is_not(None))
            .label(self.field_name)
        )

        def parse(result: Any) -> list:
            return [{"value": v.value, "label": v.display} for v in result] if result else []

        return bundle, parse

    def facets_columns(self) -> tuple[Bundle | ColumnElement, Callable]:
        bundle, _ = self.specs_columns()

        def parse(result: Any) -> list:
            return result if result else []

        return bundle, parse

    async def specs(self, session: AsyncSession, query: Select) -> list:
        field = getattr(self.model, self.field).label("value")
        query = (
            query.with_only_columns(field)
            .where(field.is_not(None))
            .order_by(field.asc())
            .distinct()
        )
        result = (await session.execute(query)).unique().scalars().all()
        return [{"value": v.value, "label": v.display} for v in result]

    async def facets(self, session: AsyncSession, query: Select) -> list[str]:
        return [v["value"] for v in await self.specs(session, query)]


class EnumInFilter(EnumFilter):
    """Фильтр по вхождению enum в список"""

    def filter(self, query: Select, value: Sequence) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query

        expression = getattr(self.model, self.field).in_(value)
        return query.where(~expression if self.exclude else expression)


class DatePartFilter(Filter):
    """Фильтр по опредленной части даты"""

    has_specs: bool = True
    has_facets: bool = True
    has_specs_columns: bool = True
    has_facets_columns: bool = True

    def __init__(
        self,
        model: Type[BaseClass],
        field: str,
        *,
        date_part: str,
        exclude: bool = False,
        nullable: bool = False,
    ) -> None:
        """
        :param model: Модель для фильтрации
        :param field: Поле модели для фильтрации
        :param date_part: часть даты (год, месяц...)
        :param exclude: Производить инвертированную фильтрацию
        :param nullable: Допускать пустые значения
        """
        super().__init__(model=model, field=field, exclude=exclude, nullable=nullable)
        self.date_part = date_part

    def filter(self, query: Select, value: Any) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query

        expression = sa.extract(self.date_part, getattr(self.model, self.field)) == value
        return query.where(~expression if self.exclude else expression)

    def specs_columns(self) -> tuple[Bundle | ColumnElement, Callable]:
        field = getattr(self.model, self.field)
        date_part: ColumnElement = sa.cast(
            sa.extract(self.date_part, field),
            sa.Integer,
        ).label("date_part")

        bundle = (
            func.array_agg(aggregate_order_by(sa.distinct(date_part), date_part.desc()))
            .filter(field.is_not(None))
            .label(self.field_name)
        )

        def parse(result: Any) -> list:
            return [{"value": v, "label": v} for v in result] if result else []

        return bundle, parse

    def facets_columns(self) -> tuple[Bundle | ColumnElement, Callable]:
        field = getattr(self.model, self.field)
        date_part: ColumnElement = sa.cast(
            sa.extract(self.date_part, field),
            sa.Integer,
        ).label("date_part")

        bundle = (
            func.array_agg(aggregate_order_by(sa.distinct(date_part), date_part.desc()))
            .filter(field.is_not(None))
            .label(self.field_name)
        )

        def parse(result: Any) -> list:
            return result if result else []

        return bundle, parse

    async def facets(self, session: AsyncSession, query: Select) -> list[int]:
        field = getattr(self.model, self.field)
        date_part: ColumnElement = sa.cast(
            sa.extract(self.date_part, field),
            sa.Integer,
        ).label("date_part")
        query = query.with_only_columns(date_part).distinct().order_by(date_part.desc())
        result = await session.execute(query)
        return result.unique().scalars().all()

    async def specs(self, session: AsyncSession, query: Select) -> list[dict]:
        return [{"value": v, "label": v} for v in await self.facets(session, query)]


class DatePartInFilter(DatePartFilter):
    """Фильтр по вхождению определнной части даты в список"""

    def filter(self, query: Select, value: Any) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query

        expression = sa.extract(
            self.date_part,
            getattr(self.model, self.field),
        ).in_(value)
        return query.where(~expression if self.exclude else expression)


class YearMonthFilter(Filter):
    """Фильтр по году и месяцу в формате 'yyyy-mm'"""

    has_specs: bool = True
    has_facets: bool = True
    has_specs_columns: bool = True
    has_facets_columns: bool = True

    def __init__(
        self,
        model: Type[BaseClass],
        field: str,
        *,
        specs_schema: Type[Sequence[BaseModel]] = list[ChoiceSchema],
        exclude: bool = False,
        nullable: bool = False,
    ) -> None:
        """
        :param model: Модель для фильтрации
        :param field: Поле модели для фильтрации
        :param specs_schema: Сериализатор спеков
        :param exclude: Производить инвертированную фильтрацию
        :param nullable: Допускать пустые значения
        """
        super().__init__(model=model, field=field, exclude=exclude, nullable=nullable)
        self.specs_schema = specs_schema

    def filter(self, query: Select, value: Any) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query

        field = getattr(self.model, self.field)
        year_part, month_part = sa.extract("year", field), sa.func.to_char(field, sa.text("'MM'"))
        value_field = sa.func.concat(year_part, sa.text("'-'"), month_part)
        expression = value_field == value
        return query.where(~expression if self.exclude else expression)

    def specs_columns(self) -> tuple[Bundle | ColumnElement, Callable]:
        field = getattr(self.model, self.field)
        year, month = sa.extract("year", field), sa.func.to_char(field, sa.text("'MM'"))
        date_part = sa.func.concat(year, sa.text("'-'"), month)

        bundle = (
            func.array_agg(aggregate_order_by(sa.distinct(date_part), date_part.desc()))
            .filter(field.is_not(None))
            .label(self.field_name)
        )

        def parse(result: Any) -> list:
            if not result:
                return []
            result = ({"value": value, "label": f"{value}-01"} for value in result)
            choices = parse_obj_as(self.specs_schema, result)
            return [choice.dict() for choice in choices]

        return bundle, parse

    def facets_columns(self) -> tuple[Bundle | ColumnElement, Callable]:
        bundle, _ = self.specs_columns()

        def parse(result: Any) -> dict:
            return result if result else []

        return bundle, parse

    async def specs(self, session: AsyncSession, query: Select) -> list[dict[str, str]]:
        field = getattr(self.model, self.field)
        year, month = sa.extract("year", field), sa.func.to_char(field, sa.text("'MM'"))
        value_field: ColumnElement = sa.distinct(sa.func.concat(year, sa.text("'-'"), month)).label(
            "value"
        )
        label_field: ColumnElement = sa.func.concat(
            year, sa.text("'-'"), month, sa.text("'-01'")
        ).label("label")
        query = query.with_only_columns(value_field, label_field).order_by(value_field.desc())
        result = (await session.execute(query)).all()
        choices = parse_obj_as(self.specs_schema, result)
        return [choice.dict() for choice in choices]

    async def facets(self, session: AsyncSession, query: Select) -> list[str]:
        field = getattr(self.model, self.field)
        year, month = sa.extract("year", field), sa.func.to_char(field, sa.text("'MM'"))
        value_field: ColumnElement = sa.distinct(sa.func.concat(year, sa.text("'-'"), month)).label(
            "value"
        )
        query = query.with_only_columns(value_field).order_by(value_field.desc())
        return (await session.execute(query)).unique().scalars().all()


class RangeFilter(Filter):
    """Фильтр по диапазону"""

    has_specs: bool = True
    has_facets: bool = True
    has_specs_columns: bool = True
    has_facets_columns: bool = True

    def __init__(
        self,
        model: Type[BaseClass],
        field: str,
        *,
        specs_schema: Type[BaseModel] = NumberFilterSpecsSchema,
        exclude: bool = False,
        nullable: bool = False,
    ) -> None:
        """
        :param model: Модель для фильтрации
        :param field: Поле модели для фильтрации
        :param specs_schema: Сериализатор спеков
        :param exclude: Производить инвертированную фильтрацию
        :param nullable: Допускать пустые значения
        """
        super().__init__(model=model, field=field, exclude=exclude, nullable=nullable)
        self.specs_schema = specs_schema

    def filter(self, query: Select, value: Any) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query
        min_value, max_value = value

        expressions = []
        column = getattr(self.model, self.field)
        if min_value is not None:
            expressions.append(column >= min_value)
        if max_value is not None:
            expressions.append(column <= max_value)
        expression = sa.and_(*expressions)
        return query.where(~expression if self.exclude else expression)

    def specs_columns(self) -> tuple[Bundle | ColumnElement, Callable]:
        bundle = Bundle(
            self.field_name,
            sa.func.min(getattr(self.model, self.field)).label(f"min_{self.field_name}"),
            sa.func.max(getattr(self.model, self.field)).label(f"max_{self.field_name}"),
        )

        def parse(result: Any) -> dict:
            data = {
                "min": getattr(result, f"min_{self.field_name}"),
                "max": getattr(result, f"max_{self.field_name}"),
            }
            return parse_obj_as(self.specs_schema, data).dict()

        return bundle, parse

    def facets_columns(self) -> tuple[Bundle | ColumnElement, Callable]:
        return self.specs_columns()

    async def specs(self, session: AsyncSession, query: Select) -> dict:
        field = getattr(self.model, self.field)
        min_value = sa.func.min(field).label("min_value")
        max_value = sa.func.max(field).label("max_value")
        query = query.with_only_columns(min_value, max_value)
        min_value, max_value = (await session.execute(query)).one()
        data = {"min": min_value, "max": max_value}
        return parse_obj_as(self.specs_schema, data).dict()

    async def facets(self, session: AsyncSession, query: Select) -> dict:
        return await self.specs(session, query)


class NumberFilter(RangeFilter):
    """Фильтр по числу"""

    def __init__(
        self,
        model: Type[BaseClass],
        field: str,
        *,
        specs_schema: Type[BaseModel] = NumberFilterSpecsSchema,
        operator: Callable = operators.eq,
        exclude: bool = False,
        nullable: bool = False,
    ) -> None:
        """
        :param model: Модель для фильтрации
        :param field: Поле модели для фильтрации
        :param specs_schema: Сериализатор спеков
        :param operator: Оператор сравнения из модуля operator
        :param exclude: Производить инвертированную фильтрацию
        :param nullable: Допускать пустые значения
        """
        super().__init__(model=model, field=field, exclude=exclude, nullable=nullable)
        self.specs_schema = specs_schema
        self.operator = operator

    def filter(self, query: Select, value: Any) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query

        expression = self.operator(getattr(self.model, self.field), value)
        return query.where(~expression if self.exclude else expression)


class BooleanFilter(Filter):
    """Фильтр по булевому значeнию"""

    has_specs: bool = True
    has_facets: bool = True
    has_specs_columns: bool = True
    has_facets_columns: bool = True

    def filter(self, query: Select, value: Any) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query

        expression = getattr(self.model, self.field).is_(value)
        return query.where(~expression if self.exclude else expression)

    def specs_columns(self) -> tuple[Bundle | ColumnElement, Callable]:
        field = getattr(self.model, self.field)
        bundle = (
            func.array_agg(aggregate_order_by(func.distinct(field), field.desc()))
            .filter(field.is_not(None))
            .label(self.field_name)
        )

        def parse(result: Any) -> list:
            return result if result else []

        return bundle, parse

    def facets_columns(self) -> tuple[Bundle | ColumnElement, Callable]:
        return self.specs_columns()

    async def specs(self, session: AsyncSession, query: Select) -> list[bool]:
        field = getattr(self.model, self.field).label("value")
        query = (
            query.with_only_columns(field)
            .where(field.is_not(None))
            .order_by(field.asc())
            .distinct()
        )
        return (await session.execute(query)).unique().scalars().all()

    async def facets(self, session: AsyncSession, query: Select) -> list[bool]:
        return await self.specs(session, query)


class CheckboxFilter(Filter):
    """Фильтр "Галка" по булевому значeнию."""

    has_specs = True
    has_facets = True
    has_specs_columns = False
    has_facets_columns = True

    def filter(self, query: Select, value: Any) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query
        value = value if not self.exclude else not value
        expression = getattr(self.model, self.field).is_(value)
        return query.where(expression)

    def facets_columns(self) -> tuple[Bundle | ColumnElement, Callable]:
        field = getattr(self.model, self.field)
        value = True if not self.exclude else False
        bundle: ColumnElement = sa.case(
            [[func.count(field).filter(field.is_(value)) > sa.text("0"), sa.true()]],
            else_=sa.false(),
        ).label(self.field_name)

        def parse(result: Any) -> bool:
            return result

        return bundle, parse

    async def specs(self, session: AsyncSession, query: Select) -> bool:
        return True

    async def facets(self, session: AsyncSession, query: Select) -> bool:
        return True


class ILikeFilter(BaseFilter):
    """Фильтр по поиску в списке полей"""

    def __init__(
        self,
        model: Type[BaseClass],
        *fields: str,
        exclude: bool = False,
        nullable: bool = False,
    ) -> None:
        """
        :param model: Модель для фильтрации
        :param fields: Список полей для поиска
        :param exclude: Производить инвертированную фильтрацию
        :param nullable: Допускать пустые значения
        """
        super().__init__()
        self.model = model
        self.fields = fields
        self.exclude = exclude
        self.nullable = nullable

    def filter(self, query: Select, value: Any) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query

        if "*" in value or "_" in value:
            looking_for = value.replace("_", "__").replace("*", "%").replace("?", "_")
        else:
            looking_for = "%{0}%".format(value)
        expression = sa.or_(
            *[
                cast(getattr(self.model, field), sa.String).ilike(looking_for)
                for field in self.fields
            ]
        )
        return query.where(~expression if self.exclude else expression)


class OrderingFilter(BaseFilter):
    """Фильтр для управления сортировкой результатов"""

    def __init__(self, fields: dict[str, tuple[Type[BaseClass] | None, str]]) -> None:
        """
        :param fields: Словарь полей, по которым можно производить сортировку. Ключ -
        название поля в фильтре, значение - вариант кортежа: или Модель с именем
        поля или None.
        """
        super().__init__()
        self.fields = fields

    def filter(self, query: Select, value: list[str]) -> Select:
        if not value:
            return query

        query = query.order_by()
        for v in value:
            reverse = v.startswith("-")
            sort_func = sa.desc if reverse else sa.asc
            v = v[1:] if reverse else v

            if v in EMPTY_VALUES or v not in self.fields:
                continue

            model, field = self.fields[v]
            if model and isinstance(field, str):
                query = query.order_by(sort_func(getattr(model, field)))
            else:
                query = query.order_by(sort_func(field))
        return query


class LimitOffsetPagination(BaseFilter):
    """Фильтр для управления limit и offset"""

    def filter(self, query: Select, values: Sequence[int]) -> Select:
        offset, limit = values
        return query.offset(offset).limit(limit)


class MethodFilter(BaseFilter):
    """Фильтр с возможностью задать методы: фильтрации, получения спеков и фасетов в
    родительском FilterSet"""

    def __init__(
        self,
        method: str,
        facets: str | None = None,
        specs: str | None = None,
        specs_columns: str | None = None,
        facets_columns: str | None = None,
    ) -> None:
        """
        :param method: Название метода в родительском FilterSet, для фильтрации
        :param facets: Название метода в родительском FilterSet, для получения спеков
        :param specs: Название метода в родительском FilterSet, для получения фасетов
        :param facets_columns: Название метода в родительском FilterSet, для спеков в колонке
        :param specs_columns: Название метода в родительском FilterSet, для фасетов в колонке
        """
        super().__init__()
        self.has_specs = bool(specs)
        self.has_facets = bool(facets)
        self.has_specs_columns = bool(specs_columns)
        self.has_facets_columns = bool(facets_columns)
        self.method = method
        self.specs_method = specs
        self.facets_method = facets
        self.specs_columns_method = specs_columns
        self.facets_columns_method = facets_columns
        self._filter: Callable | None = None
        self._specs: Callable | None = None
        self._facets: Callable | None = None
        self._specs_columns: Callable | None = None
        self._facets_columns: Callable | None = None

    @property
    def parent(self) -> Optional["IFilterSet"]:
        return self._parent

    @parent.setter
    def parent(self, value: "IFilterSet") -> None:
        self._parent = value
        self.init_filter_methods()

    def init_filter_methods(self) -> None:
        from src.common.filters.filterset import BaseFilterSet

        assert isinstance(self.parent, BaseFilterSet)

        assert hasattr(self.parent, self.method)
        self._filter = getattr(self.parent, self.method)

        if self.specs_method:
            self._specs = getattr(self.parent, self.specs_method)

        if self.facets_method:
            self._facets = getattr(self.parent, self.facets_method)

        if self.specs_columns_method:
            self._specs_columns = getattr(self.parent, self.specs_columns_method)

        if self.facets_columns_method:
            self._facets_columns = getattr(self.parent, self.facets_columns_method)

    def filter(self, query: Select, value: Any) -> Select:
        assert self._filter

        if value in EMPTY_VALUES:
            return query

        return self._filter(query, value)

    async def specs(self, session: AsyncSession, query: Select) -> Any:
        assert self._specs

        return await self._specs(session, query)

    async def facets(self, session: AsyncSession, query: Select) -> Any:
        assert self._facets

        return await self._facets(session, query)

    def specs_columns(self) -> Any:
        assert self._specs_columns

        return self._specs_columns()

    def facets_columns(self) -> Any:
        assert self._facets_columns

        return self._facets_columns()


class ChangedWithRelatedFilter(Filter):
    """
    Фильтр по полю changed в модели и в релейшн моделях
    Если в релейшн модели или родительской модели
    поле входит в заданный min_changed max_changed,
    то оно будет выведено
    """

    def __init__(
        self,
        model: Type[BaseClass],
        relation_fields: list[tuple[str, bool]],  # relation field name, needs outerjoin
        field: str = "changed",
    ):
        super().__init__(model=model, field=field)
        self.relation_fields = relation_fields

    def filter(self, query: Select, value: Any) -> Select:
        if value in EMPTY_VALUES:
            return query
        for relation_field_name, needs_join in self.relation_fields:
            if needs_join is True:
                query = query.outerjoin(getattr(self.model, relation_field_name))

        min_changed, max_changed = value
        expression = None

        if min_changed is not None and max_changed is not None:
            sub_ands = []
            for relation_field_name, _ in self.relation_fields:
                relation_model = getattr(self.model, relation_field_name).entity.entity
                sub_ands.append(
                    sa.and_(
                        getattr(relation_model, self.field) >= min_changed,
                        getattr(relation_model, self.field) <= max_changed,
                    )
                )
            expression = sa.or_(
                sa.and_(
                    getattr(self.model, self.field) >= min_changed,
                    getattr(self.model, self.field) <= max_changed,
                ),
                *sub_ands,
            )

        else:
            if min_changed is not None:
                expression = sa.or_(
                    getattr(self.model, self.field) >= min_changed,
                    *[
                        getattr(
                            getattr(self.model, relation).entity.entity,
                            self.field,
                        )
                        >= min_changed
                        for relation, _ in self.relation_fields
                    ],
                )
            if max_changed is not None:
                expression = sa.or_(
                    getattr(self.model, self.field) <= max_changed,
                    *[
                        getattr(
                            getattr(self.model, relation).entity.entity,
                            self.field,
                        )
                        <= max_changed
                        for relation, _ in self.relation_fields
                    ],
                )

        if expression is not None:
            filtered_query = query.filter(expression)
            return filtered_query
        else:
            return query
