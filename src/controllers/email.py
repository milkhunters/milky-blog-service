import time
from random import randint

from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi import Response
from fastapi import BackgroundTasks

from models.role import UserStates
from utils.exceptions import APIError

from utils.mail import MailManager
from database import crud
from models import schemas
from utils.validations import is_valid_email

router = APIRouter(prefix="/email", tags=["Email"], responses={"4xx": {"model": schemas.ExceptionsAPIModel}})


@router.post("/send/")
async def send_email(email: str, request: Request, background_tasks: BackgroundTasks):
    if not is_valid_email(email):
        raise APIError(902)

    # Check if email exists
    user = await crud.get_user(email=email)
    if user is None:
        raise APIError(904)

    # Chech if user already confirmed
    if user.state != UserStates.not_confirmed:
        raise APIError(912)

    keys = await request.app.state.redis.keys(pattern=f'{email}*')
    if keys:
        data_key = keys[0].split(':')
        if int(data_key[1]) > int(time.time()) - 120:
            raise APIError(914)
        await request.app.state.redis.delete(keys[0])

    code = randint(100000, 999900)
    await request.app.state.redis.set(f"""{email}:{int(time.time())}:0""", code)
    background_tasks.add_task(MailManager().send_confirm_code, email, code)
    return {"message": "Сообщение отправлено"}


@router.post("/confirm/")
async def confirm_email(email: str, code: int, request: Request):
    if not is_valid_email(email):
        raise APIError(902)

    user = await crud.get_user(email=email)
    if not user:
        raise APIError(904)

    if user.state != UserStates.not_confirmed:
        raise APIError(912)

    keys = await request.app.state.redis.keys(pattern=f'{email}*')
    if not keys:
        raise APIError(915)

    data_key = keys[0].split(':')  # (email, timestamp, attempts)
    if int(data_key[1]) < int(time.time()) - 86400:
        raise APIError(913)

    if int(data_key[2]) > 3:
        raise APIError(916)

    code_in_db = await request.app.state.redis.get(keys[0])
    if int(code_in_db) != code:
        await request.app.state.redis.delete(keys[0])
        await request.app.state.redis.set(f"""{data_key[0]}:{int(data_key[1])}:{int(data_key[2]) + 1}""", code)
        raise APIError(911)

    user.state = UserStates.active
    await user.save()
    await request.app.state.redis.delete(keys[0])
    return {"message": "Email подтвержден"}
