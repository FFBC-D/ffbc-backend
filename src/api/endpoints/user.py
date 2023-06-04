from dataclasses import asdict

from fastapi import APIRouter

from src.common.dependencies.current_authenticated_user import CurrentAuthenticatedUser
from src.domain.user.dto.output import UserOutSchema

router = APIRouter()


@router.get("/me", status_code=200, response_model=UserOutSchema)
async def current_user_route(user: CurrentAuthenticatedUser):
    return UserOutSchema.parse_obj(asdict(user))
