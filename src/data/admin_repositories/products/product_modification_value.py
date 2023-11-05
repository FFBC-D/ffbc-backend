from sqlalchemy import select

from src.common.filters import FilterSet, Filter, ILikeFilter, RangeFilter
from src.common.repository import BaseRepo
from src.data.database.models.product import ProductModificationValue
from src.domain.products.product_modification.dto.admin import ProductModificationAdminFilterSchema


class ProductModificationValueAdminFilterSet(FilterSet):
    id = Filter(ProductModificationValue, "id")
    name = ILikeFilter(ProductModificationValue, "name")
    price = RangeFilter(ProductModificationValue, "price")
    modification_id = Filter(ProductModificationValue, "modification_id")


class ProductModificationValueAdminRepo(
    BaseRepo[ProductModificationValue, ProductModificationAdminFilterSchema]
):
    model = ProductModificationValue
    query = select(ProductModificationValue)
    filter_set = ProductModificationValueAdminFilterSet
