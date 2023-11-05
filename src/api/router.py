from fastapi import APIRouter

from src.api.admin_endpoints.products.measure_category import MeasureCategoryAdminRouter
from src.api.admin_endpoints.products.measure_value import MeasureValueAdminRouter
from src.api.admin_endpoints.products.product import ProductAdminRouter
from src.api.admin_endpoints.products.product_category import ProductCategoryAdminRouter
from src.api.admin_endpoints.products.product_modification import ProductModificationAdminRouter
from src.api.admin_endpoints.products.product_modification_value import (
    ProductModificationValueAdminRouter,
)
from src.api.admin_endpoints.user import UserAdminRouter
from src.api.endpoints import register_router, auth_router, user_router
from src.common.admin.api.extra_actions_router import AdminExtraActionsRouter


def include_admin_endpoint_routers() -> APIRouter:
    endpoint_router = AdminExtraActionsRouter()

    endpoint_router.include_router(UserAdminRouter(), prefix="/users", tags=["Admin User"])
    endpoint_router.include_router(
        MeasureCategoryAdminRouter(),
        prefix="/measure-categories",
        tags=["Admin Measure Category"],
    )
    endpoint_router.include_router(
        MeasureValueAdminRouter(), prefix="/measure-values", tags=["Admin Measure Value"]
    )
    endpoint_router.include_router(ProductAdminRouter(), prefix="/products", tags=["Admin Product"])
    endpoint_router.include_router(
        ProductCategoryAdminRouter(),
        prefix="/product-categories",
        tags=["Admin Product Category"],
    )
    endpoint_router.include_router(
        ProductModificationAdminRouter(),
        prefix="/product-modifications",
        tags=["Admin Product Modification"],
    )
    endpoint_router.include_router(
        ProductModificationValueAdminRouter(),
        prefix="/product-modification-values",
        tags=["Admin Product Modification Value"],
    )

    return endpoint_router


def include_endpoint_routers() -> APIRouter:
    endpoint_router = APIRouter()

    endpoint_router.include_router(register_router, prefix="/register", tags=["Registration"])
    endpoint_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
    endpoint_router.include_router(user_router, prefix="/users", tags=["User"])

    return endpoint_router
