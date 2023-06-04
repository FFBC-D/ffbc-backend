from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar, Callable, Awaitable

from choicesenum import ChoicesEnum
from fastapi import Query

from src.common.types.python_types import IdType


class APIMethod(ChoicesEnum):
    list_view = "list_view"
    create_view = "create_view"
    retrieve_view = "retrieve_view"
    update_view = "update_view"
    delete_view = "delete_view"
    update_files_view = "update_file_links_view"


class HTTPMethod(ChoicesEnum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    DELETE = "DELETE"


class AnnotationKey(str, Enum):
    QUERIES = "queries"
    NEW_OBJECT = "new_object"
    OBJECT_ID = "object_id"
    UPDATED_OBJECT = "updated_object"


@dataclass
class AdminQueries(Generic[IdType]):
    id: list[IdType] | None = Query(None)
    _sort: str | None = Query(None)
    _order: str | None = Query("ASC", regex="^(ASC|DESC)$")
    _start: int = Query(0)
    _end: int = Query(10)

    def __post_init__(self) -> None:
        self._ids: list[IdType] | None = self.id
        self.id = None

    @property
    def pagination(self) -> tuple[int, int]:
        return self._start, (self._end - self._start) if self._end > self._start else 0

    @property
    def order(self) -> list[str] | None:
        prefix = "-" if self._order == "DESC" else ""
        return [f"{prefix}{self._sort}"] if self._sort else None

    @property
    def ids(self) -> list[IdType] | None:
        return self._ids


QueriesType = TypeVar("QueriesType", bound=AdminQueries)
IUseCase = TypeVar("IUseCase")
DependencyProvider = Callable[..., IUseCase | Awaitable[IUseCase]]
