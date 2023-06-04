from dataclasses import dataclass
from uuid import UUID

from dependency_injector.wiring import Provider, inject, Provide
from fastapi import Query, Depends
from starlette import status
from starlette.responses import Response

from src.common.admin.api.base_router import BaseAdminRouter
from src.common.admin.api.decorators import action
from src.common.admin.api.types import AdminQueries, HTTPMethod
from src.common.dependencies.current_admin_user import CurrentAdminUser
from src.data.database.models.user import User
from src.domain.user.admin_use_cases.change_password import ChangePasswordAdmin
from src.domain.user.admin_use_cases.create_user import CreateUserAdmin
from src.domain.user.dto.admin import (
    UserAdminFilterSchema,
    UserAdminCreateSchema,
    UserAdminUpdateSchema,
    UserAdminListSchema,
    UserAdminOutSchema,
    UserAdminUpdatePasswordSchema,
)


@dataclass
class UserAdminQueries(AdminQueries[UUID]):
    email: str | None = Query(None, description="Email")
    phone: str | None = Query(None, description="Phone")


class UserAdminRouter(
    BaseAdminRouter[
        UUID,
        User,
        UserAdminFilterSchema,
        UserAdminQueries,
    ]
):
    entity_class = User
    list_schema = UserAdminListSchema
    retrieve_schema = UserAdminOutSchema
    create_schema = UserAdminCreateSchema
    update_schema = UserAdminUpdateSchema
    filter_schema = UserAdminFilterSchema
    queries = UserAdminQueries
    repository_attr_name = "user_admin"
    create_use_case = CreateUserAdmin
    uow_factory = Provider["repositories.uow"]  # type: ignore

    @action(
        url_path="/{object_id}/change-password",
        method=HTTPMethod.POST,
        status_code=status.HTTP_200_OK,
        in_schema=UserAdminUpdatePasswordSchema,
        summary="Change user password",
    )
    @inject
    async def change_password(
        self,
        _: CurrentAdminUser,
        object_id: int,
        new_object: UserAdminUpdatePasswordSchema,
        change_password: ChangePasswordAdmin = Depends(Provide["use_cases.change_password_admin"]),
    ) -> Response:
        await change_password(object_id, new_object)
        return Response(status_code=status.HTTP_200_OK)
