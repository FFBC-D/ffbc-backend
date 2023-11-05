from sqlalchemy import select

from src.common.filters import FilterSet, Filter, ILikeFilter
from src.common.repository import BaseRepo
from src.data.database.models.product import MeasureValue
from src.domain.products.measure_value.dto.admin import MeasureValueAdminFilterSchema


class MeasureValueAdminFilterSet(FilterSet):
    id = Filter(MeasureValue, "id")
    name = ILikeFilter(MeasureValue, "name")
    category_id = Filter(MeasureValue, "category_id")


class MeasureValueAdminRepo(BaseRepo[MeasureValue, MeasureValueAdminFilterSchema]):
    model = MeasureValue
    query = select(MeasureValue)
    filter_set = MeasureValueAdminFilterSet
