from dataclasses import dataclass
from decimal import Decimal

from dependency_injector.wiring import Provider
from fastapi import Query

from src.common.admin.api.base_router import BaseAdminRouter
from src.common.admin.api.types import AdminQueries
from src.data.database.models.product import Product
from src.domain.products.product.dto.admin import (
    ProductAdminFilterSchema,
    ProductOutSchema,
    ProductAdminCreateSchema,
    ProductAdminUpdateSchema,
    ProductListSchema,
)


@dataclass
class ProductAdminQueries(AdminQueries[int]):
    name: str | None = Query(None, description="Name")
    base_price: Decimal | None = Query(None, description="Base price")
    product_category_id: int | None = Query(None, description="Category ID")


class ProductAdminRouter(
    BaseAdminRouter[
        int,
        Product,
        ProductAdminFilterSchema,
        ProductAdminQueries,
    ]
):
    entity_class = Product
    list_schema = ProductListSchema
    retrieve_schema = ProductOutSchema
    create_schema = ProductAdminCreateSchema
    update_schema = ProductAdminUpdateSchema
    filter_schema = ProductAdminFilterSchema
    queries = ProductAdminQueries
    repository_attr_name = "product_admin"
    uow_factory = Provider["repositories.uow"]  # type: ignore
