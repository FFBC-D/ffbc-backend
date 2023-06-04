from datetime import datetime

from pydantic import BaseModel

from src.common.dto import OrmModel
from src.domain.jwt_token.enums import JwtTokenType


class JwtTokenSchema(OrmModel):
    token_type: JwtTokenType
    jti: str
    user_id: int
    exp: datetime


class JwtTokensOutSchema(BaseModel):
    access_token: str
    refresh_token: str
