from fastapi import APIRouter, Depends
from starlette.requests import Request

from exceptions import APIError
from services.auth.auth import send_verify_code, verify_email

from utils import validators
import views

router = APIRouter(
    # responses={"4xx": {"model": schemas.ExceptionsAPIModel}}
)

"""
TODO:
    3. Стандартизировать ответы
"""


@router.post("/send/", responses={200: {"message": "Сообщение отправлено"}})
async def send_email(email: str, request: Request):
    if not validators.is_valid_email(email):
        raise APIError(902)
    rabbitmq = request.app.state.rabbitmq
    await send_verify_code(rabbitmq, email)
    return {"message": "Сообщение отправлено"}
    # TODO: подумать над ответом пользователю


@router.post("/confirm/", responses={200: {"message": "Email подтвержден"}})
async def confirm_email(email: str, code: int):
    if not validators.is_valid_email(email):
        raise APIError(902)
    await verify_email(email, code)
    return {"message": "Email подтвержден"}
