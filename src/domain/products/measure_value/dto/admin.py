from src.common.dto import BaseOutSchema, OrmModel, BaseInSchema


class MeasureValueAdminBaseInSchema(BaseInSchema):
    name: str
    category_id: int


class MeasureValueAdminCreateSchema(MeasureValueAdminBaseInSchema):
    pass


class MeasureValueAdminUpdateSchema(MeasureValueAdminBaseInSchema):
    pass


class MeasureValueOutSchema(BaseOutSchema):
    name: str


class MeasureValueListSchema(MeasureValueOutSchema):
    pass


class MeasureValueAdminFilterSchema(OrmModel):
    id: int | None = None
    name: str | None = None
    category_id: int | None = None
