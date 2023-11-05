from dataclasses import dataclass

from dependency_injector.wiring import Provider
from fastapi import Query

from src.common.admin.api.base_router import BaseAdminRouter
from src.common.admin.api.types import AdminQueries
from src.data.database.models.product import MeasureValue
from src.domain.products.measure_value.dto.admin import (
    MeasureValueListSchema,
    MeasureValueAdminCreateSchema,
    MeasureValueAdminUpdateSchema,
    MeasureValueOutSchema,
    MeasureValueAdminFilterSchema,
)


@dataclass
class MeasureValueAdminQueries(AdminQueries[int]):
    name: str | None = Query(None, description="Name")
    category_id: int | None = Query(None, description="Category ID")


class MeasureValueAdminRouter(
    BaseAdminRouter[
        int,
        MeasureValue,
        MeasureValueAdminFilterSchema,
        MeasureValueAdminQueries,
    ]
):
    entity_class = MeasureValue
    list_schema = MeasureValueListSchema
    retrieve_schema = MeasureValueOutSchema
    create_schema = MeasureValueAdminCreateSchema
    update_schema = MeasureValueAdminUpdateSchema
    filter_schema = MeasureValueAdminFilterSchema
    queries = MeasureValueAdminQueries
    repository_attr_name = "measure_value_admin"
    uow_factory = Provider["repositories.uow"]  # type: ignore
