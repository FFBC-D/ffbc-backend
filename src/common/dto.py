from pydantic import BaseModel


class OrmModel(BaseModel):
    class Config:
        orm_mode = True


class BaseOutSchema(OrmModel):
    id: int | None


class BaseInSchema(OrmModel):
    pass
