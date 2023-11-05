from dataclasses import dataclass

from dependency_injector.wiring import Provider
from fastapi import Query

from src.common.admin.api.base_router import BaseAdminRouter
from src.common.admin.api.types import AdminQueries
from src.data.database.models.product import ProductModification
from src.domain.products.product_modification.dto.admin import (
    ProductModificationListSchema,
    ProductModificationAdminCreateSchema,
    ProductModificationOutSchema,
    ProductModificationAdminUpdateSchema,
    ProductModificationAdminFilterSchema,
)


@dataclass
class ProductModificationAdminQueries(AdminQueries[int]):
    name: str | None = Query(None, description="Name")
    product_categories: list[int] = Query(None, description="Product categories")


class ProductModificationAdminRouter(
    BaseAdminRouter[
        int,
        ProductModification,
        ProductModificationAdminFilterSchema,
        ProductModificationAdminQueries,
    ]
):
    entity_class = ProductModification
    list_schema = ProductModificationListSchema
    retrieve_schema = ProductModificationOutSchema
    create_schema = ProductModificationAdminCreateSchema
    update_schema = ProductModificationAdminUpdateSchema
    filter_schema = ProductModificationAdminFilterSchema
    queries = ProductModificationAdminQueries
    repository_attr_name = "product_modification_admin"
    uow_factory = Provider["repositories.uow"]  # type: ignore
