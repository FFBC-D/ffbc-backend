from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import Body, Depends

from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.http_exceptions import AppHTTPException
from src.data.database.models.user import User
from src.domain.jwt_token.enums import JwtTokenType
from src.domain.jwt_token.use_cases.decode_jwt_token import DecodeJwtToken
from src.domain.user.dto.filter import UserFilterSchema
from src.domain.user.use_cases.retrieve_user import RetrieveUser


@inject
async def get_current_user_from_refresh_token(
    refresh_token: str = Body(..., embed=True),
    decode_jwt_token: DecodeJwtToken = Depends(Provide["use_cases.decode_jwt_token"]),
    retrieve_user: RetrieveUser = Depends(Provide["use_cases.retrieve_user"]),
) -> User | None:
    decoded_token, token_in_blacklist = await decode_jwt_token(
        token=refresh_token, token_type=JwtTokenType.REFRESH
    )
    if token_in_blacklist:
        raise AppHTTPException(
            status_code=400,
            error_code=ErrorCode.AUTH_ERROR,
            message="Invalid token",
        )

    return await retrieve_user(data=UserFilterSchema(id=decoded_token.user_id))


CurrentUserFromRefreshToken = Annotated[User, Depends(get_current_user_from_refresh_token)]
