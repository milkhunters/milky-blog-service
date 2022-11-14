import random
import time

from starlette.requests import Request
from starlette.responses import Response

import utils
from exceptions.api import APIError
from models import schemas
from models.state import UserStates
from services.repository import UserRepo
from utils import RedisClient
from . import JWTManager, SessionManager
from ..user import UserService
from ..email import EmailService
# TODO: исправить импорты


async def authenticate(
        login: str,
        password: str,
        response: Response,
        jwt: JWTManager = JWTManager(),
        session: SessionManager = SessionManager(),
        user_service: UserService = UserService()
):
    """
    Аутентификация пользователя
    :param login:
    :param password:
    :param response:
    :param user_repo:
    :param jwt:
    :param session:
    :param user_service:
    :return:
    """

    user = await user_service.get_user(username=login)
    if not user:
        raise APIError(904)
    if not utils.verify_password(password, user.hashed_password):
        raise APIError(905)
    if user.state == UserStates.not_confirmed:
        raise APIError(907)
    if user.state == UserStates.blocked:
        raise APIError(906)
    if user.state == UserStates.deleted:
        raise APIError(904)

    # установка токенов
    tokens = schemas.Tokens(
        access_token=jwt.generate_access_token(user.id, user.username, user.role_id, user.state.value),
        refresh_token=jwt.generate_refresh_token(user.id, user.username, user.role_id, user.state.value)
    )
    jwt.set_jwt_cookie(response, tokens)
    await session.set_session_id(response, tokens.refresh_token)
    return user


async def logout(
        request: Request,
        response: Response,
        jwt: JWTManager = JWTManager(),
        session: SessionManager = SessionManager()
):
    """
    Выход из аккаунта
    :param request:
    :param response:
    :param jwt:
    :param session:
    :return:
    """
    jwt.delete_jwt_cookie(response)
    await session.delete_session_id(session.get_session_id(request), response)


async def refresh_tokens(
        request: Request,
        response: Response,
        jwt: JWTManager = JWTManager(),
        session: SessionManager = SessionManager()
):
    """
    Обновление токенов
    :param request:
    :param response:
    :param user_repo:
    :param jwt:
    :param session:
    :return:
    """
    current_tokens = jwt.get_jwt_cookie(request)
    session_id = session.get_session_id(request)
    user = await UserRepo().get(id=jwt.decode_refresh_token(current_tokens.refresh_token).id)

    if not (user.state == UserStates.active):
        raise APIError(906)

    new_payload = schemas.TokenPayload(
        id=user.id,
        username=user.username,
        state_id=user.state.value,
        role_id=user.role_id,
        exp=0
    )  # exp не используется, но нужно для составления модели

    new_tokens = schemas.Tokens(
        access_token=jwt.generate_access_token(**new_payload.dict()),
        refresh_token=jwt.generate_refresh_token(**new_payload.dict())
    )
    jwt.set_jwt_cookie(response, new_tokens)
    # Для бесшовного обновления токенов:
    request.cookies["access_token"] = new_tokens.access_token
    request.cookies["refresh_token"] = new_tokens.refresh_token

    await session.set_session_id(response, new_tokens.refresh_token, session_id)


async def send_verify_code(
        rabbitmq,
        email: str,
        user_service: UserService = UserService(),
        email_service: EmailService = EmailService(),
        redis: RedisClient = RedisClient()
) -> None:
    """
    Отправляет код подтверждения email
    Сам код генерируется внутри метода

    :param rabbitmq:
    :param email: почта пользователя.
    :param user_service: пользовательский сервис.
    :param email_service: сервис отправки почты.
    :param redis: клиент redis.

    """
    # Проверка на существование пользователя
    user = await user_service.get_user(email=email)
    if user is None:
        raise APIError(904)

    # Проверка, что пользователь не подтвержден
    if user.state != UserStates.not_confirmed:
        raise APIError(912)

    keys = await redis.keys(pattern=f'{email}*')
    if keys:
        key_map = keys[0].split(':')
        create_time = int(key_map[1])
        if create_time > int(time.time()) - 120:
            raise APIError(914)
        await redis.delete(keys[0])

    code = random.randint(100000, 999990)
    await redis.set(f"""{email}:{int(time.time())}:0""", str(code), expire=1000)
    # TODO: подгружать html шаблон из файла
    await email_service.send_mail(rabbitmq, email, 'Подтверждение почты', f'Ваш код подтверждения: {code}')


async def verify_email(
        email: str,
        code: int,
        user_service: UserService = UserService(),
        redis: RedisClient = RedisClient()
):
    """
    Подтверждает почту пользователя.

    :param email: почта пользователя.
    :param code: код подтверждения.
    :param user_service: пользовательский сервис.
    :param email_service: сервис отправки почты.
    :param redis: клиент redis.

    """

    user = await user_service.get_user(email=email)
    if not user:
        raise APIError(904)

    if user.state != UserStates.not_confirmed:
        raise APIError(912)

    keys = await redis.keys(pattern=f'{email}*')
    if not keys:
        raise APIError(915)

    key_map = keys[0].split(':')  # (email, timestamp, attempts)
    email = key_map[0]
    create_time = int(key_map[1])
    attempts = int(key_map[2])

    if create_time < int(time.time()) - 86400:
        raise APIError(913)

    if attempts > 3:
        raise APIError(916)

    code_in_redis = int(await redis.get(keys[0]))
    if code_in_redis != code:
        await redis.delete(keys[0])
        await redis.set(f"{email}:{create_time}:{attempts + 1}", str(code_in_redis))
        raise APIError(911)

    await user_service.update_user(user.id, state=UserStates.active)
    await redis.delete(keys[0])


async def send_password_reset_link(
        email: str,
        user_service: UserService = UserService(),
        email_service: EmailService = EmailService()
):
    """
    Отправляет ссылку для сброса пароля на почту

    :param email: почта пользователя.
    :param user_service: пользовательский сервис.
    :param email_service: сервис отправки почты.

    """
    ...


async def verify_password_reset_code(
        email: str,
        code: str,
        user_service: UserService = UserService(),
        email_service: EmailService = EmailService()
) -> bool:
    """
    Проверяет код для сброса пароля

    :param email: почта пользователя.
    :param code: код подтверждения от пользователя.
    :param user_service: пользовательский сервис.
    :param email_service: сервис отправки почты.

    """
    ...
