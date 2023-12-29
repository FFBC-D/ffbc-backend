from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.responses import Response

from src.api.dependencies.current_user_from_refresh_token import CurrentUserFromRefreshToken
from src.domain.jwt_token.dto.output import JwtTokensOutSchema
from src.domain.jwt_token.enums import JwtTokenType
from src.domain.jwt_token.use_cases.add_jwt_tokens_to_blacklist import AddJwtTokensToBlacklist
from src.domain.jwt_token.use_cases.create_jwt_tokens import CreateJwtTokens
from src.domain.jwt_token.use_cases.decode_jwt_token import DecodeJwtToken
from src.domain.user.dto.input import AuthInSchema
from src.domain.user.use_cases.authenticate import Authenticate
from src.utils.auth import get_token_from_bearer_string

router = APIRouter()


@router.post("/access-token", status_code=200, response_model=JwtTokensOutSchema)
@inject
async def access_token_route(
    data: AuthInSchema,
    authenticate: Authenticate = Depends(Provide["use_cases.authenticate"]),
    create_jwt_tokens: CreateJwtTokens = Depends(Provide["use_cases.create_jwt_tokens"]),
):
    user = await authenticate(data)
    return await create_jwt_tokens(user_id=user.id)


@router.post("/refresh-token", status_code=200, response_model=JwtTokensOutSchema)
@inject
async def refresh_token_route(
    current_user: CurrentUserFromRefreshToken,
    create_jwt_tokens: CreateJwtTokens = Depends(Provide["use_cases.create_jwt_tokens"]),
    add_jwt_tokens_to_blacklist: AddJwtTokensToBlacklist = Depends(
        Provide["use_cases.add_jwt_tokens_to_blacklist"]
    ),
):
    await add_jwt_tokens_to_blacklist(user_id=current_user.id)
    return await create_jwt_tokens(user_id=current_user.id)


@router.post("/revoke-token", status_code=204)
@inject
async def revoke_token_route(
    auth_credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    decode_jwt_token: DecodeJwtToken = Depends(Provide["use_cases.decode_jwt_token"]),
    add_jwt_tokens_to_blacklist: AddJwtTokensToBlacklist = Depends(
        Provide["use_cases.add_jwt_tokens_to_blacklist"]
    ),
):
    token = get_token_from_bearer_string(bearer_string=auth_credentials.credentials)
    decoded_token, token_in_blacklist = await decode_jwt_token(
        token=token, token_type=JwtTokenType.ACCESS
    )
    if token_in_blacklist:
        return Response(status_code=204)

    await add_jwt_tokens_to_blacklist(user_id=decoded_token.user_id)
    return Response(status_code=204)
