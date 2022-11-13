import logging

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import Response

from services import UserService
from config import load_docs
from dependencies import JWTCookie
from exceptions.api import APIError

from services.auth import authenticate, logout, refresh_tokens
from views import LoginResponse, RegisterResponse
from exceptions.models import ErrorAPIResponse
from models import schemas


router = APIRouter(responses={"400": {"model": ErrorAPIResponse}})
docs = load_docs("auth.ini")


@router.post(
    "/signUp",
    response_model=RegisterResponse,
    summary=docs["signUp"]["summary"],
    description=docs["signUp"]["description"]
)
async def sign_up(
        data: schemas.UserCreate,
        is_auth=Depends(JWTCookie(auto_error=False)),
):
    user_service = UserService()

    if is_auth:
        raise APIError(920)
    return await user_service.create_user(data)


@router.post(
    "/signIn",
    response_model=LoginResponse,
    summary=docs["signIn"]["summary"],
    description=docs["signIn"]["description"]
)
async def sign_in(
        user: schemas.UserAuth,
        response: Response,
        is_auth=Depends(JWTCookie(auto_error=False))
):
    if is_auth:
        raise APIError(920)
    return await authenticate(user.username, user.password, response)


@router.post(
    '/logout',
    dependencies=[Depends(JWTCookie())],
    summary=docs["logout"]["summary"],
    description=docs["logout"]["description"]
)
async def logout_controller(request: Request, response: Response):
    await logout(request, response)


@router.post(
    '/refresh_tokens',
    dependencies=[Depends(JWTCookie())],
    summary=docs["refresh_tokens"]["summary"],
    description=docs["refresh_tokens"]["description"]
)
async def refresh(request: Request, response: Response):
    await refresh_tokens(request, response)
