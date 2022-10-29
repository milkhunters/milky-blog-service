import logging

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import Response

from models import schemas
from src.config import load_docs
from src.dependencies import JWTCookie
from src.exceptions.api import APIError
from src.services.auth import logout
from views import ErrorAPIResponse
from views import UserResponse
from views import UserOutResponse

from src.services import repository

router = APIRouter(responses={"400": {"model": ErrorAPIResponse}})
docs = load_docs("user.ini")


@router.get("/current", dependencies=[Depends(JWTCookie())], response_model=UserResponse)
async def get_current_user(request: Request):
    user_repo = repository.UserRepo()

    user = await user_repo.get(id=request.user.id)
    if not user:
        raise APIError(api_code=404)
    return user


@router.get("/{user_id}", response_model=UserOutResponse)
async def get_user(user_id: int):
    user_repo = repository.UserRepo()

    user = await user_repo.get(id=user_id)
    if not user:
        raise APIError(api_code=904)
    return user


@router.post("/update", dependencies=[Depends(JWTCookie())], response_model=UserResponse)
async def update_user(data: schemas.UserUpdate, request: Request):
    user_repo = repository.UserRepo()

    await user_repo.update(request.user.id, **data.dict(exclude_unset=True))
    return await user_repo.get(id=request.user.id)


@router.delete("/delete", dependencies=[Depends(JWTCookie())])
async def delete_user(request: Request, response: Response):
    user_repo = repository.UserRepo()

    await logout(request, response)
    await user_repo.delete(request.user.id)
