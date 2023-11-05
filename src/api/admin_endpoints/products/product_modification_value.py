from dataclasses import dataclass
from decimal import Decimal

from dependency_injector.wiring import Provider
from fastapi import Query

from src.common.admin.api.base_router import BaseAdminRouter
from src.common.admin.api.types import AdminQueries
from src.data.database.models.product import ProductModificationValue
from src.domain.products.product_modification_value.dto.admin import (
    ProductModificationValueListSchema,
    ProductModificationValueOutSchema,
    ProductModificationValueAdminCreateSchema,
    ProductModificationValueAdminUpdateSchema,
    ProductModificationValueAdminFilterSchema,
)


@dataclass
class ProductModificationValueAdminQueries(AdminQueries[int]):
    name: str | None = Query(None, description="Name")
    price: Decimal | None = Query(None, description="Price")
    measure_id: int | None = Query(None, description="Measure ID")


class ProductModificationValueAdminRouter(
    BaseAdminRouter[
        int,
        ProductModificationValue,
        ProductModificationValueAdminFilterSchema,
        ProductModificationValueAdminQueries,
    ]
):
    entity_class = ProductModificationValue
    list_schema = ProductModificationValueListSchema
    retrieve_schema = ProductModificationValueOutSchema
    create_schema = ProductModificationValueAdminCreateSchema
    update_schema = ProductModificationValueAdminUpdateSchema
    filter_schema = ProductModificationValueAdminFilterSchema
    queries = ProductModificationValueAdminQueries
    repository_attr_name = "product_modification_admin"
    uow_factory = Provider["repositories.uow"]  # type: ignore
