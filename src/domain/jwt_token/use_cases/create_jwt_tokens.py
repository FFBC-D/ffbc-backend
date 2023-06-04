from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import uuid4

from jose import jwt

from src.data.database.models.jwt import OutstandingToken
from src.data.uow import UnitOfWork
from src.domain.jwt_token.dto.output import JwtTokensOutSchema, JwtTokenSchema
from src.domain.jwt_token.enums import JwtTokenType


@dataclass
class CreateJwtTokens:
    uow: UnitOfWork
    config: dict

    def _encode_payload(self, token_data: JwtTokenSchema) -> str:
        encoded_jwt = jwt.encode(
            token_data.dict(),
            self.config["secret_key"],
            algorithm=self.config["jwt_algorithm"],
        )
        return encoded_jwt

    async def __call__(self, user_id: int) -> JwtTokensOutSchema:
        access_jti = uuid4().hex
        refresh_jti = uuid4().hex

        access_exp = datetime.utcnow() + timedelta(
            minutes=self.config["access_token_expires_minutes"]
        )
        refresh_exp = datetime.utcnow() + timedelta(
            minutes=self.config["refresh_token_expires_minutes"]
        )

        access_token_payload = JwtTokenSchema(
            user_id=user_id,
            token_type=JwtTokenType.ACCESS,
            exp=access_exp,
            jti=access_jti,
        )
        refresh_token_payload = JwtTokenSchema(
            user_id=user_id,
            token_type=JwtTokenType.REFRESH,
            exp=refresh_exp,
            jti=refresh_jti,
        )

        async with self.uow:
            access_token = OutstandingToken(
                jti=access_jti,
                user_id=user_id,
                expires_at=access_exp,
                token=self._encode_payload(access_token_payload),
            )
            refresh_token = OutstandingToken(
                jti=refresh_jti,
                user_id=user_id,
                expires_at=refresh_exp,
                token=self._encode_payload(refresh_token_payload),
            )
            await self.uow.outstanding_token.add_all(access_token, refresh_token)
            await self.uow.commit()

        return JwtTokensOutSchema(
            access_token=access_token.token, refresh_token=refresh_token.token
        )
