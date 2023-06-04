from datetime import datetime

from pydantic import BaseModel, validator

from src.common.dto import OrmModel


class DatetimeFilterSpecsSchema(OrmModel):
    min: datetime | None
    max: datetime | None


class NumberFilterSpecsSchema(OrmModel):
    min: float | None
    max: float | None


class ChoiceSchema(OrmModel):
    value: str
    label: str


class OrderingFilterSchemaMixin(BaseModel):
    ordering: list[str] | None = None

    @validator("ordering", pre=False, always=True)
    def default_ordering(cls, value: list[str] | None) -> list[str]:
        if value is None or "id" in value:
            return ["id"]
        else:
            ordering = value + ["id"]
            return ordering
