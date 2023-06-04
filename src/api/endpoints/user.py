from dataclasses import asdict

from fastapi import APIRouter, Depends

from src.common.admin.dependencies.current_user import get_current_authenticated_user
from src.data.database.models.user import User
from src.domain.user.dto.output import UserOutSchema

router = APIRouter()


@router.get("/me", status_code=200, response_model=UserOutSchema)
async def current_user_route(user: User = Depends(get_current_authenticated_user)):
    return UserOutSchema.parse_obj(asdict(user))
