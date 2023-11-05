from decimal import Decimal

from src.common.dto import BaseOutSchema, OrmModel, BaseInSchema


class ProductModificationValueAdminBaseInSchema(BaseInSchema):
    name: str
    price: Decimal
    modification_id: int


class ProductModificationValueAdminCreateSchema(ProductModificationValueAdminBaseInSchema):
    pass


class ProductModificationValueAdminUpdateSchema(ProductModificationValueAdminBaseInSchema):
    pass


class ProductModificationValueOutSchema(BaseOutSchema):
    name: str
    price: Decimal
    modification_id: int


class ProductModificationValueListSchema(ProductModificationValueOutSchema):
    pass


class ProductModificationValueAdminFilterSchema(OrmModel):
    id: int | None = None
    name: str | None = None
    price: Decimal | None = None
    modification_id: int | None = None
