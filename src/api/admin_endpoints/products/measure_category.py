from dataclasses import dataclass

from dependency_injector.wiring import Provider
from fastapi import Query

from src.common.admin.api.base_router import BaseAdminRouter
from src.common.admin.api.types import AdminQueries
from src.data.database.models.product import MeasureCategory
from src.domain.products.measure_category.dto.admin import (
    MeasureCategoryAdminCreateSchema,
    MeasureCategoryAdminUpdateSchema,
    MeasureCategoryAdminFilterSchema,
    MeasureCategoryOutSchema,
    MeasureCategoryListSchema,
)


@dataclass
class MeasureCategoryAdminQueries(AdminQueries[int]):
    name: str | None = Query(None, description="Name")
    product_categories: list[int] = Query(None, description="Product categories")


class MeasureCategoryAdminRouter(
    BaseAdminRouter[
        int,
        MeasureCategory,
        MeasureCategoryAdminFilterSchema,
        MeasureCategoryAdminQueries,
    ]
):
    entity_class = MeasureCategory
    list_schema = MeasureCategoryListSchema
    retrieve_schema = MeasureCategoryOutSchema
    create_schema = MeasureCategoryAdminCreateSchema
    update_schema = MeasureCategoryAdminUpdateSchema
    filter_schema = MeasureCategoryAdminFilterSchema
    queries = MeasureCategoryAdminQueries
    repository_attr_name = "measure_category_admin"
    uow_factory = Provider["repositories.uow"]  # type: ignore
