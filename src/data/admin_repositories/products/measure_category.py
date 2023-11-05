from sqlalchemy import select, Select

from src.common.filters import FilterSet, Filter, ILikeFilter, MethodFilter
from src.common.repository import BaseRepo
from src.data.database.models.product import MeasureCategory, ProductCategoryMeasureCategory
from src.domain.products.measure_category.dto.admin import MeasureCategoryAdminFilterSchema


class MeasureCategoryAdminFilterSet(FilterSet):
    id = Filter(MeasureCategory, "id")
    name = ILikeFilter(MeasureCategory, "name")
    product_categories = MethodFilter("filter_product_categories")

    def filter_product_categories(self, query: Select, values: list[int]) -> Select:
        return query.join(ProductCategoryMeasureCategory).filter(
            ProductCategoryMeasureCategory.product_category_id.in_(values)
        )


class MeasureCategoryAdminRepo(BaseRepo[MeasureCategory, MeasureCategoryAdminFilterSchema]):
    model = MeasureCategory
    query = select(MeasureCategory)
    filter_set = MeasureCategoryAdminFilterSet
