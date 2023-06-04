from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from src.domain.user.dto.input import RegisterInSchema
from src.domain.user.use_cases.register import Register

router = APIRouter()


@router.post("/", status_code=201)
@inject
async def register_user_route(
    data: RegisterInSchema, register: Register = Depends(Provide["use_cases.register"])
):
    await register(data)
    return {"msg": "Check email"}
