import uuid

from fastapi import APIRouter, Depends
from fastapi import status as http_status
from fastapi.requests import Request
from fastapi.responses import Response

from src.dependencies.services import get_services
from src.models import schemas
from src.services import ServiceFactory

from src.views.user import UserResponse, UserSmallResponse

router = APIRouter()


@router.get("/current", response_model=UserResponse, status_code=http_status.HTTP_200_OK)
async def get_current_user(services: ServiceFactory = Depends(get_services)):
    return UserResponse(content=await services.user.get_me())


@router.put("/update", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def update_current_user(data: schemas.UserUpdate, services: ServiceFactory = Depends(get_services)):
    await services.user.update_me(data)

#
# @router.put("/update/password", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
# async def update_password():
#     await services.user.update_password(new_hashed_password, old_hashed_password, new_enc_private_key)


@router.get("/{user_id}", response_model=UserSmallResponse, status_code=http_status.HTTP_200_OK)
async def get_user(user_id: uuid.UUID, services: ServiceFactory = Depends(get_services)):
    return UserSmallResponse(content=await services.user.get_user(user_id))


@router.delete("/delete", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_current_user(
        password: str,
        request: Request,
        response: Response,
        services: ServiceFactory = Depends(get_services)
):
    await services.user.delete_me(password)
    await services.auth.logout(request, response)
