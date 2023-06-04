import abc
import inspect
from typing import Any, Callable, Generic, Type

from dependency_injector.wiring import inject
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from starlette.responses import Response

from src.common.admin.api.types import APIMethod, AdminQueries, QueriesType, AnnotationKey
from src.common.admin.interfaces import (
    IAdminListUseCase,
    IAdminCreateUseCase,
    IAdminRetrieveUseCase,
    IAdminUpdateFilesUseCase,
    IAdminDeleteUseCase,
    IAdminUpdateUseCase,
)
from src.common.admin.use_cases.create import AdminCreateUseCase
from src.common.admin.use_cases.delete import AdminDeleteUseCase
from src.common.admin.use_cases.list import AdminListUseCase
from src.common.admin.use_cases.retrieve import AdminRetrieveUseCase
from src.common.admin.use_cases.update import AdminUpdateUseCase
from src.common.admin.use_cases.update_files import AdminUpdateFilesUseCase
from src.common.dependencies.current_admin_user import get_current_admin_user, CurrentAdminUser
from src.common.dto import OrmModel, BaseOutSchema
from src.common.repository import ModelEntity
from src.common.types.python_types import IdType, AdminFilterSchema, SchemaInType
from src.common.uow import BaseUnitOfWork
from src.data.database.models.user import User


class BaseAdminRouter(
    Generic[IdType, ModelEntity, AdminFilterSchema, QueriesType],
    abc.ABC,
    APIRouter,
):
    methods: list = APIMethod.values()

    id_type: Type = int
    uow_factory: Callable[..., BaseUnitOfWork]
    repository_attr_name: str
    entity_class: Type[ModelEntity]

    queries: Type[AdminQueries] = AdminQueries
    filter_schema: Type[OrmModel] = AdminFilterSchema

    list_schema: Type[BaseOutSchema]
    retrieve_schema: Type[BaseOutSchema]
    create_schema: Type[SchemaInType]
    update_schema: Type[SchemaInType]
    files_update_schema: Type[SchemaInType] | None = None

    list_use_case: Callable[..., IAdminListUseCase] = AdminListUseCase
    create_use_case: Callable[..., IAdminCreateUseCase] = AdminCreateUseCase
    retrieve_use_case: Callable[..., IAdminRetrieveUseCase] = AdminRetrieveUseCase
    update_use_case: Callable[..., IAdminUpdateUseCase] = AdminUpdateUseCase
    delete_use_case: Callable[..., IAdminDeleteUseCase] = AdminDeleteUseCase
    update_files_use_case: Callable[..., IAdminUpdateFilesUseCase] = AdminUpdateFilesUseCase

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.add_endpoints()

    def add_endpoints(self) -> None:
        crud_views: dict[str, Callable] = {
            APIMethod.list_view: self.add_list_endpoint,
            APIMethod.create_view: self.add_create_endpoint,
            APIMethod.retrieve_view: self.add_retrieve_endpoint,
            APIMethod.update_view: self.add_update_endpoint,
            APIMethod.delete_view: self.add_delete_endpoint,
        }

        if self.files_update_schema:
            crud_views[APIMethod.update_files_view] = self.add_update_file_links_endpoint

        for view_name, add_view_method in crud_views.items():
            if view_name in self.methods:
                add_view_method()

    def add_list_endpoint(self) -> None:
        @inject
        async def list_view(
            _: CurrentAdminUser, queries: QueriesType = Depends()
        ) -> list[ModelEntity]:
            use_case = await self._list_use_case_factory()
            try:
                schema = self.filter_schema.from_orm(queries)
            except ValidationError as e:
                raise HTTPException(
                    detail=e.errors(), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
                )

            results = await use_case(schema)
            return results  # type: ignore

        list_view.__annotations__[AnnotationKey.QUERIES] = self.queries

        self.add_api_route(
            "",
            endpoint=list_view,
            summary="List",
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            response_model=list[self.list_schema],  # type: ignore
        )

    def add_create_endpoint(self) -> None:
        async def create_view(new_object: SchemaInType, _: CurrentAdminUser) -> ModelEntity:
            use_case = await self._create_use_case_factory()
            return await use_case(new_object=new_object)

        create_view.__annotations__[AnnotationKey.NEW_OBJECT] = self.create_schema

        self.add_api_route(
            "",
            create_view,
            summary="Create",
            methods=["POST"],
            response_model=self.retrieve_schema,
            status_code=status.HTTP_201_CREATED,
        )

    def add_retrieve_endpoint(self) -> None:
        async def retrieve_view(object_id: IdType, _: CurrentAdminUser) -> ModelEntity:
            use_case = await self._retrieve_use_case_factory()
            return await use_case(object_id)

        retrieve_view.__annotations__[AnnotationKey.OBJECT_ID] = self.id_type

        self.add_api_route(
            "/{object_id}",
            endpoint=retrieve_view,
            summary="Detail",
            response_model=self.retrieve_schema,
        )

    def add_update_endpoint(self) -> None:
        async def update_view(
            object_id: IdType, updated_object: SchemaInType, _: CurrentAdminUser
        ) -> ModelEntity:
            use_case = await self._update_use_case_factory()
            return await use_case(object_id, updated_object)

        update_view.__annotations__[AnnotationKey.UPDATED_OBJECT] = self.update_schema

        self.add_api_route(
            "/{object_id}",
            update_view,
            summary="Update",
            methods=["PATCH"],
            status_code=status.HTTP_200_OK,
            response_model=self.retrieve_schema,
        )

    def add_delete_endpoint(self) -> None:
        async def delete_view(object_id: IdType, _: CurrentAdminUser) -> Response:
            use_case = await self._delete_use_case_factory()
            await use_case(object_id)
            return Response(status_code=status.HTTP_204_NO_CONTENT)  # type: ignore

        delete_view.__annotations__[AnnotationKey.OBJECT_ID] = self.id_type

        self.add_api_route(
            "/{object_id}",
            endpoint=delete_view,
            summary="Delete",
            methods=["DELETE"],
            status_code=status.HTTP_204_NO_CONTENT,
        )

    def add_update_file_links_endpoint(self) -> None:
        async def update_file_links_view(
            object_id: IdType, data: SchemaInType, _: CurrentAdminUser
        ) -> ModelEntity:
            use_case = await self._update_file_links_use_case_factory()
            return await use_case(object_id, data)

        update_file_links_view.__annotations__[
            AnnotationKey.UPDATED_OBJECT
        ] = self.files_update_schema

        self.add_api_route(
            "/{object_id}/update-files",
            endpoint=update_file_links_view,
            summary="Upload file links",
            methods=["PATCH"],
            status_code=status.HTTP_200_OK,
        )

    async def _list_use_case_factory(self) -> IAdminListUseCase:
        use_case = self.list_use_case(
            uow=self.uow_factory(),
            repository_attr_name=self.repository_attr_name,
        )
        if inspect.isawaitable(use_case):
            await use_case
        return use_case

    async def _create_use_case_factory(self) -> IAdminCreateUseCase:
        use_case = self.create_use_case(
            uow=self.uow_factory(),
            repository_attr_name=self.repository_attr_name,
            entity_class=self.entity_class,
        )
        if inspect.isawaitable(use_case):
            use_case = await use_case
        return use_case

    async def _retrieve_use_case_factory(self) -> IAdminRetrieveUseCase:
        use_case = self.retrieve_use_case(
            uow=self.uow_factory(),
            repository_attr_name=self.repository_attr_name,
            filter_schema_class=self.filter_schema,
        )
        if inspect.isawaitable(use_case):
            use_case = await use_case
        return use_case

    async def _update_use_case_factory(self) -> IAdminUpdateUseCase:
        use_case = self.update_use_case(
            uow=self.uow_factory(),
            repository_attr_name=self.repository_attr_name,
            filter_schema_class=self.filter_schema,
        )
        if inspect.isawaitable(use_case):
            use_case = await use_case
        return use_case

    async def _delete_use_case_factory(self) -> IAdminDeleteUseCase:
        use_case = self.delete_use_case(
            uow=self.uow_factory(),
            repository_attr_name=self.repository_attr_name,
            filter_schema_class=self.filter_schema,
        )
        if inspect.isawaitable(use_case):
            use_case = await use_case
        return use_case

    async def _update_file_links_use_case_factory(self) -> IAdminUpdateFilesUseCase:
        use_case = self.update_files_use_case(
            uow=self.uow_factory(),
            repository_attr_name=self.repository_attr_name,
            filter_schema_class=self.filter_schema,
        )
        if inspect.isawaitable(use_case):
            use_case = await use_case
        return use_case
