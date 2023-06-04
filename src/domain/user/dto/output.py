from datetime import datetime

from src.common.dto import BaseOutSchema


class UserOutSchema(BaseOutSchema):
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    birth_date: datetime | None = None
    street: str | None = None
    city: str | None = None
    country: str | None = None
