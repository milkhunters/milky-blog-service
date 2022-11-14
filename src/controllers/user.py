import logging

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import Response

from models import schemas
from config import load_docs
from dependencies import JWTCookie
from exceptions.api import APIError
from services.auth import logout
from exceptions.models import ErrorAPIResponse
import views

from services import UserService

router = APIRouter(responses={"400": {"model": ErrorAPIResponse}})
docs = load_docs("user.ini")


@router.get("/current", dependencies=[Depends(JWTCookie())], response_model=views.UserResponse)
async def get_current_user(request: Request):
    user_service = UserService()

    user = await user_service.get_user(request.user.id)
    if not user:
        raise APIError(api_code=919)
    return user


@router.get("/{user_id}", response_model=views.UserOutResponse)
async def get_user(user_id: int):
    user_service = UserService()

    user = await user_service.get_user(user_id)
    if not user:
        raise APIError(api_code=904)
    return user


@router.post("/update", dependencies=[Depends(JWTCookie())], response_model=views.UserResponse)
async def update_user(data: schemas.UserUpdate, request: Request):
    user_service = UserService()

    await user_service.update_user(request.user.id, **data.dict(exclude_unset=True))


@router.delete("/delete", dependencies=[Depends(JWTCookie())])
async def delete_user(request: Request, response: Response):
    user_service = UserService()

    await logout(request, response)
    await user_service.delete_user(request.user.id)
