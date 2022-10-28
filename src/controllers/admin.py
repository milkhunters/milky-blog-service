from random import randint

from fastapi import APIRouter, File, UploadFile, Depends
from fastapi import Request
from fastapi import Response

from dependencies.auth_bearer import JWTCookie
from dependencies.role_filter import MinRoleFilter
from models.role import Role
from models.role import MainRole as M
from models.role import AdditionalRole as A
from utils.exceptions import APIError
from tortoise.expressions import Q

from models.schemas import ExceptionsAPIModel
from utils.auth.jwt import JWTManager
from utils.auth import verify_password
from src.database import crud
from models import schemas

router = APIRouter(
    tags=["Admin"],
    prefix="/admin",
    dependencies=[Depends(JWTCookie()), Depends(MinRoleFilter(31))],
    responses={"4xx": {"model": ExceptionsAPIModel}}
)


@router.get("/getUser/{user_id}", response_model=schemas.User)
async def get_user(user_id: int):
    user = await crud.get_user(id=user_id)
    if not user:
        raise APIError(904)
    return user
