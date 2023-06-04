from dataclasses import dataclass

from jose import jwt
from pydantic import ValidationError

from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.use_case_exceptions import UseCaseHTTPException
from src.data.uow import UnitOfWork
from src.domain.jwt_token.dto.filter import OutstandingTokenFilterSchema, BlacklistTokenFilterSchema
from src.domain.jwt_token.dto.output import JwtTokenSchema
from src.domain.jwt_token.enums import JwtTokenType


@dataclass
class DecodeJwtToken:
    uow: UnitOfWork
    config: dict

    async def __call__(self, token: str, token_type: JwtTokenType) -> tuple[JwtTokenSchema, bool]:
        try:
            payload = jwt.decode(
                token, self.config["secret_key"], algorithms=[self.config["jwt_algorithm"]]
            )
            decoded_token = JwtTokenSchema(**payload)
        except (jwt.JWTError, ValidationError):
            raise UseCaseHTTPException(
                error_code=ErrorCode.AUTH_ERROR,
                message="Could not validate credentials",
            )

        token_in_blacklist = False
        async with self.uow:
            outstanding_token = await self.uow.outstanding_token.retrieve(
                OutstandingTokenFilterSchema(jti=decoded_token.jti, user_id=decoded_token.user_id)
            )
            blacklist_token = await self.uow.blacklist_token.first(
                BlacklistTokenFilterSchema(outstanding_token_id=outstanding_token.id)
            )
            if blacklist_token:
                token_in_blacklist = True

            if decoded_token.token_type != token_type:
                raise UseCaseHTTPException(
                    error_code=ErrorCode.AUTH_ERROR,
                    message="Token has incorrect type",
                )

        return decoded_token, token_in_blacklist
