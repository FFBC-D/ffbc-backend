from src.common.dto import OrmModel


class OutstandingTokenFilterSchema(OrmModel):
    jti: str | None = None
    user_id: int | None = None
    in_blacklist: bool | None = False


class BlacklistTokenFilterSchema(OrmModel):
    outstanding_token_id: int | None = None
