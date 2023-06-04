from enum import Enum
from inspect import getmembers
from typing import Callable, Optional, Dict, List, Union, Type, Sequence, Any

from fastapi import APIRouter, params
from fastapi.datastructures import Default
from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id
from starlette.responses import Response, JSONResponse
from starlette.routing import BaseRoute

from src.common.admin.api.decorators import ActionMapper


def _is_extra_action(attr):
    return hasattr(attr, "mapper")


class AdminExtraActionsRouter(APIRouter):
    def include_router(
        self,
        router: "APIRouter",
        *,
        prefix: str = "",
        tags: Optional[List[Union[str, Enum]]] = None,
        dependencies: Optional[Sequence[params.Depends]] = None,
        default_response_class: Type[Response] = Default(JSONResponse),
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        callbacks: Optional[List[BaseRoute]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        generate_unique_id_function: Callable[[APIRoute], str] = Default(generate_unique_id),
    ) -> None:
        super().include_router(
            router=router,
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
            default_response_class=default_response_class,
            responses=responses,
            callbacks=callbacks,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            generate_unique_id_function=generate_unique_id_function,
        )

        extra_actions = [method for _, method in getmembers(router, _is_extra_action)]
        for extra_action in extra_actions:
            action_params: ActionMapper = extra_action.mapper

            for key, value in action_params.annotations.items():
                if value is None:
                    continue

                extra_action.__annotations__[key] = value

            self.add_api_route(
                action_params.url_path,
                extra_action,
                summary=action_params.summary,
                methods=[action_params.method.value],
                status_code=action_params.status_code,
                response_model=action_params.response_model,
                tags=tags,
            )
