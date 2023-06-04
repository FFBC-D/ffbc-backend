from src.common.dto import OrmModel


class UserFilterSchema(OrmModel):
    id: int | None = None
    email: str | None = None
