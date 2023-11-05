from decimal import Decimal

from src.common.dto import BaseOutSchema, OrmModel, BaseInSchema


class ProductAdminBaseInSchema(BaseInSchema):
    name: str
    base_price: Decimal
    price_multiplier: Decimal
    description: str
    video: str | None
    product_category_id: int


class ProductAdminCreateSchema(ProductAdminBaseInSchema):
    pass


class ProductAdminUpdateSchema(ProductAdminBaseInSchema):
    pass


class ProductOutSchema(BaseOutSchema):
    name: str
    base_price: Decimal
    price_multiplier: Decimal
    description: str
    video: str | None
    product_category_id: int


class ProductListSchema(BaseOutSchema):
    name: str
    base_price: Decimal
    price_multiplier: Decimal
    product_category_id: int


class ProductAdminFilterSchema(OrmModel):
    id: int | None = None
    name: str | None = None
    base_price: Decimal | None = None
    product_category_id: int | None = None
