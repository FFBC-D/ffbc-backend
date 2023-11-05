from src.common.dto import BaseOutSchema, OrmModel, BaseInSchema


class MeasureCategoryAdminBaseInSchema(BaseInSchema):
    name: str


class MeasureCategoryAdminCreateSchema(MeasureCategoryAdminBaseInSchema):
    pass


class MeasureCategoryAdminUpdateSchema(MeasureCategoryAdminBaseInSchema):
    pass


class MeasureCategoryOutSchema(BaseOutSchema):
    name: str


class MeasureCategoryListSchema(MeasureCategoryOutSchema):
    pass


class MeasureCategoryAdminFilterSchema(OrmModel):
    id: int | None = None
    name: str | None = None
    product_categories: list[int] | None = None
