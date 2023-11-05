from sqlalchemy import select, Select

from src.common.filters import FilterSet, Filter, ILikeFilter, MethodFilter
from src.common.repository import BaseRepo
from src.data.database.models.product import ProductModification, ProductCategoryModification
from src.domain.products.product_modification.dto.admin import ProductModificationAdminFilterSchema


class ProductModificationAdminFilterSet(FilterSet):
    id = Filter(ProductModification, "id")
    name = ILikeFilter(ProductModification, "name")
    product_categories = MethodFilter("filter_product_categories")

    def filter_product_categories(self, query: Select, values: list[int]) -> Select:
        return query.join(ProductCategoryModification).filter(
            ProductCategoryModification.product_category_id.in_(values)
        )


class ProductModificationAdminRepo(
    BaseRepo[ProductModification, ProductModificationAdminFilterSchema]
):
    model = ProductModification
    query = select(ProductModification)
    filter_set = ProductModificationAdminFilterSet
