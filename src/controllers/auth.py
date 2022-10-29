import logging

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import Response

from services import UserService
from src.config import load_docs
from src.dependencies import JWTCookie
from src.exceptions.api import APIError
from src import utils
from src.services.auth import authenticate, logout, refresh_tokens
from src.views import ErrorAPIResponse, LoginResponse, RegisterResponse
from src.models import schemas
from src.services import repository

router = APIRouter(responses={"400": {"model": ErrorAPIResponse}})
docs = load_docs("auth.ini")


@router.post(
    "/signUp",
    response_model=RegisterResponse,
    summary=docs["signUp"]["summary"],
    description=docs["signUp"]["description"]
)
async def sign_up(
        user: schemas.UserSignUp,
        is_auth=Depends(JWTCookie(auto_error=False)),
):
    user_service = UserService()

    if is_auth:
        raise APIError(920)
    if await user_service.get(username__iexact=user.username):
        raise APIError(903)
    if await user_service.get(email__iexact=user.email):
        raise APIError(922)
    return await user_service.create(**user.dict())


@router.post(
    "/signIn",
    response_model=LoginResponse,
    summary=docs["signIn"]["summary"],
    description=docs["signIn"]["description"]
)
async def sign_in(
        user: schemas.UserSignIn,
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
