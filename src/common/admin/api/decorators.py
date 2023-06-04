from functools import wraps
from typing import Callable, Type, Any, NamedTuple

from starlette import status

from src.common.admin.api.types import AdminQueries, HTTPMethod, AnnotationKey
from src.common.dto import BaseOutSchema
from src.common.types.python_types import SchemaInType, IdType


class ActionMapper(NamedTuple):
    url_path: str
    method: HTTPMethod
    status_code: int
    response_model: Type[BaseOutSchema]
    annotations: dict[str, Any]
    summary: str | None = None


def action(
    url_path: str,
    method: HTTPMethod,
    status_code: status,
    detail: bool | None = False,
    response_model: Type[BaseOutSchema] | None = None,
    queries: Type[AdminQueries] | None = None,
    in_schema: Type[SchemaInType] | None = None,
    object_id: Type[IdType] | None = None,
    summary: str | None = None,
):
    if method not in HTTPMethod.values():
        raise ValueError("Method must be one of HTTP methods")

    annotations: dict[AnnotationKey, Any] = {}

    if method.is_get:
        if detail:
            annotations[AnnotationKey.OBJECT_ID] = object_id
        else:
            annotations[AnnotationKey.QUERIES] = queries
    elif method.is_post:
        annotations[AnnotationKey.NEW_OBJECT] = in_schema
        if detail:
            annotations[AnnotationKey.OBJECT_ID] = object_id
    elif method.is_patch:
        annotations[AnnotationKey.OBJECT_ID] = object_id
        annotations[AnnotationKey.UPDATED_OBJECT] = in_schema

    def wrapper(endpoint: Callable):
        endpoint.mapper = ActionMapper(
            url_path=url_path,
            method=method,
            status_code=status_code,
            response_model=response_model,
            annotations=annotations,
            summary=summary,
        )

        @wraps(endpoint)
        async def inner(self, *args: Any, **kwargs: Any):
            await endpoint(self, *args, **kwargs)

        return inner

    return wrapper
