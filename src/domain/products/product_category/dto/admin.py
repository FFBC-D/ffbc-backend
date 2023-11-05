from src.common.dto import BaseOutSchema, OrmModel, BaseInSchema


class ProductCategoryAdminBaseInSchema(BaseInSchema):
    name: str


class ProductCategoryAdminCreateSchema(ProductCategoryAdminBaseInSchema):
    pass


class ProductCategoryAdminUpdateSchema(ProductCategoryAdminBaseInSchema):
    pass


class ProductCategoryOutSchema(BaseOutSchema):
    name: str


class ProductCategoryListSchema(ProductCategoryOutSchema):
    pass


class ProductCategoryAdminFilterSchema(OrmModel):
    id: int | None = None
    name: str | None = None
