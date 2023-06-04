from fastapi import APIRouter

from src.api.admin_endpoints.user import UserAdminRouter
from src.api.endpoints import register_router, auth_router, user_router
from src.common.admin.api.extra_actions_router import AdminExtraActionsRouter


def include_admin_endpoint_routers() -> APIRouter:
    endpoint_router = AdminExtraActionsRouter()

    endpoint_router.include_router(UserAdminRouter(), prefix="/users", tags=["Admin User"])

    return endpoint_router


def include_endpoint_routers() -> APIRouter:
    endpoint_router = APIRouter()

    endpoint_router.include_router(register_router, prefix="/register", tags=["Registration"])
    endpoint_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
    endpoint_router.include_router(user_router, prefix="/users", tags=["User"])

    return endpoint_router
