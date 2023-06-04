from datetime import datetime

from pydantic import EmailStr, Field, validator

from src.common.dto import BaseOutSchema, OrmModel, BaseInSchema


class UserAdminBaseInSchema(BaseInSchema):
    is_active: bool | None = True
    phone: str | None = None
    birth_date: datetime | None = None
    street: str | None = None
    city: str | None = None
    country: str | None = None


class UserAdminCreateSchema(UserAdminBaseInSchema):
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(..., description="Password")
    password_repeat: str = Field(..., description="Repeated password")

    @validator("password_repeat")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserAdminUpdateSchema(UserAdminBaseInSchema):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None


class UserAdminUpdatePasswordSchema(BaseInSchema):
    password: str = Field(..., description="Password")
    password_repeat: str = Field(..., description="Repeated password")

    @validator("password_repeat")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserAdminOutSchema(BaseOutSchema):
    first_name: str
    last_name: str
    is_active: bool
    email: EmailStr
    phone: str | None = None
    birth_date: datetime | None = None
    street: str | None = None
    city: str | None = None
    country: str | None = None


class UserAdminListSchema(BaseOutSchema):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    birth_date: datetime | None = None


class UserAdminFilterSchema(OrmModel):
    id: int | None = None
    email: str | None = None
    phone: str | None = None
