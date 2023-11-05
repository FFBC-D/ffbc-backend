from src.common.dto import OrmModel


class MeasureCategoryFilterSchema(OrmModel):
    id: int | None = None
    name: str | None = None
