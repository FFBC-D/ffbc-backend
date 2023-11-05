from src.common.dto import BaseOutSchema, OrmModel, BaseInSchema


class ProductModificationAdminBaseInSchema(BaseInSchema):
    name: str
    icon: str | None = None


class ProductModificationAdminCreateSchema(ProductModificationAdminBaseInSchema):
    pass


class ProductModificationAdminUpdateSchema(ProductModificationAdminBaseInSchema):
    pass


class ProductModificationOutSchema(BaseOutSchema):
    name: str
    icon: str | None = None


class ProductModificationListSchema(ProductModificationOutSchema):
    pass


class ProductModificationAdminFilterSchema(OrmModel):
    id: int | None = None
    name: str | None = None
    product_categories: list[int] | None = None
