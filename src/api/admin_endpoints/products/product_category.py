from dataclasses import dataclass

from dependency_injector.wiring import Provider, inject, Provide
from fastapi import Query, Depends
from fastapi.params import Path
from starlette import status
from starlette.responses import Response

from src.common.admin.api.base_router import BaseAdminRouter
from src.common.admin.api.decorators import action
from src.common.admin.api.types import AdminQueries, HTTPMethod
from src.common.admin.enums import ModelLinkAction
from src.common.dependencies.current_admin_user import CurrentAdminUser
from src.data.database.models.product import ProductCategory
from src.domain.products.product_category.admin_use_cases.link_measure_category import (
    AdminLinkMeasureCategoryToProductCategory,
)
from src.domain.products.product_category.dto.admin import (
    ProductCategoryAdminFilterSchema,
    ProductCategoryListSchema,
    ProductCategoryOutSchema,
    ProductCategoryAdminCreateSchema,
    ProductCategoryAdminUpdateSchema,
)


@dataclass
class ProductCategoryAdminQueries(AdminQueries[int]):
    name: str | None = Query(None, description="Name")


class ProductCategoryAdminRouter(
    BaseAdminRouter[
        int,
        ProductCategory,
        ProductCategoryAdminFilterSchema,
        ProductCategoryAdminQueries,
    ]
):
    entity_class = ProductCategory
    list_schema = ProductCategoryListSchema
    retrieve_schema = ProductCategoryOutSchema
    create_schema = ProductCategoryAdminCreateSchema
    update_schema = ProductCategoryAdminUpdateSchema
    filter_schema = ProductCategoryAdminFilterSchema
    queries = ProductCategoryAdminQueries
    repository_attr_name = "product_category_admin"
    uow_factory = Provider["repositories.uow"]  # type: ignore

    @action(
        url_path="/{object_id}/measure-category/{measure_category_id}/{action}",
        detail=True,
        method=HTTPMethod.POST,
        status_code=status.HTTP_200_OK,
        summary="Link measure category with product category",
    )
    @inject
    async def link_measure_category(
        self,
        _: CurrentAdminUser,
        object_id: int,
        measure_category_id: int,
        _action: ModelLinkAction = Path(alias="action"),
        use_case: AdminLinkMeasureCategoryToProductCategory = Depends(
            Provide["use_cases.link_measure_category_to_product_category"]
        ),
    ) -> Response:
        match _action:
            case ModelLinkAction.LINK:
                await use_case(object_id, measure_category_id)
            case ModelLinkAction.UNLINK:
                await use_case(object_id, measure_category_id, unlink=True)
            case _:
                raise ValueError("Invalid link action")

        return Response(status_code=status.HTTP_200_OK)

    @action(
        url_path="/{object_id}/modification/{modification_id}/{action}",
        detail=True,
        method=HTTPMethod.POST,
        status_code=status.HTTP_200_OK,
        summary="Link measure category with product modification",
    )
    @inject
    async def link_product_modification(
        self,
        _: CurrentAdminUser,
        object_id: int,
        modification_id: int,
        _action: ModelLinkAction = Path(alias="action"),
        use_case: AdminLinkMeasureCategoryToProductCategory = Depends(
            Provide["use_cases.link_product_modification_to_product_category"]
        ),
    ) -> Response:
        match _action:
            case ModelLinkAction.LINK:
                await use_case(object_id, modification_id)
            case ModelLinkAction.UNLINK:
                await use_case(object_id, modification_id, unlink=True)
            case _:
                raise ValueError("Invalid link action")
        return Response(status_code=status.HTTP_200_OK)
