from sqlalchemy import select

from src.common.filters import FilterSet, Filter, ILikeFilter
from src.common.repository import BaseRepo
from src.data.database.models.product import ProductCategory
from src.domain.products.product_category.dto.admin import ProductCategoryAdminFilterSchema


class ProductCategoryAdminFilterSet(FilterSet):
    id = Filter(ProductCategory, "id")
    name = ILikeFilter(ProductCategory, "name")


class ProductCategoryAdminRepo(BaseRepo[ProductCategory, ProductCategoryAdminFilterSchema]):
    model = ProductCategory
    query = select(ProductCategory)
    filter_set = ProductCategoryAdminFilterSet
