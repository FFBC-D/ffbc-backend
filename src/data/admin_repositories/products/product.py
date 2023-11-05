from sqlalchemy import select

from src.common.filters import FilterSet, Filter, ILikeFilter, NumberFilter
from src.common.repository import BaseRepo
from src.data.database.models.product import Product
from src.domain.products.product.dto.admin import ProductAdminFilterSchema


class ProductAdminFilterSet(FilterSet):
    id = Filter(Product, "id")
    name = ILikeFilter(Product, "name")
    base_price = NumberFilter(Product, "base_price")
    product_category_id = Filter(Product, "product_category_id")


class ProductAdminRepo(BaseRepo[Product, ProductAdminFilterSchema]):
    model = Product
    query = select(Product)
    filter_set = ProductAdminFilterSet
