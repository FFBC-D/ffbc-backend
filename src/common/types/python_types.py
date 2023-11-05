from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel

from src.common.database.mixins import BaseClass
from src.common.dto import OrmModel, BaseInSchema

IdType = TypeVar("IdType", int, UUID, str)
ModelEntity = TypeVar("ModelEntity", bound=BaseClass)
AdminFilterSchema = TypeVar("AdminFilterSchema", bound=OrmModel)
SchemaInType = TypeVar("SchemaInType", bound=BaseInSchema)
SpecsSchema = TypeVar("SpecsSchema", bound=BaseModel)
FacetsSchema = TypeVar("FacetsSchema", bound=BaseModel)
FilterSchema = TypeVar("FilterSchema", bound=BaseModel, contravariant=True)

Obj1IdType = TypeVar("Obj1IdType", int, UUID, str)
Obj2IdType = TypeVar("Obj2IdType", int, UUID, str)
