from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi import Response

from dependencies.jwt_barrier import JWTCookie
from dependencies.role_filter import RoleFilter
from exceptions.api import APIError

from models import schemas
from models.role import Role, MainRole as M, AdditionalRole as A
from services.user import UserService
import views

router = APIRouter()


@router.get("/getUser/{user_id}", response_model=views.UserResponse)
async def get_user(user_id: int):
    """
    Более подробный вывод пользовательских данных

    """
    user_service = UserService()

    user = await user_service.get(id=user_id)
    if not user:
        raise APIError(904)
    return user
