from pydantic import Field, EmailStr, validator

from src.common.dto import BaseInSchema


class AuthInSchema(BaseInSchema):
    email: str = Field(..., description="Email")
    password: str = Field(..., description="Password")


class RegisterInSchema(BaseInSchema):
    email: EmailStr = Field(..., description="Email")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    password: str = Field(..., description="Password")
    password_repeat: str = Field(..., description="Repeated password")

    @validator("password_repeat")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v
