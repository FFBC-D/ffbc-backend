from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, Body
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer, HTTPBearer

from src.data.database.models.user import User
from src.domain.jwt_token.enums import JwtTokenType
from src.domain.jwt_token.use_cases.decode_jwt_token import DecodeJwtToken
from src.domain.user.dto.filter import UserFilterSchema
from src.domain.user.use_cases.retrieve_user import RetrieveUser
from src.utils.auth import get_token_from_bearer_string

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/access-token")

auth_scheme = HTTPBearer()


@inject
async def get_current_user(
    auth_credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
    decode_jwt_token: DecodeJwtToken = Depends(Provide["use_cases.decode_jwt_token"]),
    retrieve_user: RetrieveUser = Depends(Provide["use_cases.retrieve_user"]),
) -> User | None:
    token = get_token_from_bearer_string(bearer_string=auth_credentials.credentials)
    decoded_token, token_in_blacklist = await decode_jwt_token(
        token=token, token_type=JwtTokenType.ACCESS
    )
    if token_in_blacklist:
        raise HTTPException(status_code=400, detail="Invalid token")
    return await retrieve_user(data=UserFilterSchema(id=decoded_token.user_id))


async def get_current_authenticated_user(user: User | None = Depends(get_current_user)) -> User:
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    return user


async def get_admin_user(user: User = Depends(get_current_authenticated_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="User is not admin")
    return user


AdminUser = Annotated[User, Depends(get_admin_user)]


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
        raise HTTPException(status_code=400, detail="Invalid token")
    return await retrieve_user(data=UserFilterSchema(id=decoded_token.user_id))
