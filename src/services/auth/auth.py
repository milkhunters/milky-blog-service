from starlette.requests import Request
from starlette.responses import Response

from src import utils
from src.exceptions.api import APIError
from src.models import UserStates, schemas
from src.services import repository
from . import JWTManager, SessionManager


async def authenticate(
        login: str,
        password: str,
        response: Response,
        jwt: JWTManager = JWTManager(),
        session: SessionManager = SessionManager()
):
    """
    Аутентификация пользователя
    :param login:
    :param password:
    :param response:
    :param user_repo:
    :param jwt:
    :param session:
    :return:
    """

    user = await repository.user.get_user(username=login)
    if not user:
        raise APIError(904)
    if not utils.verify_password(password, user.hashed_password):
        raise APIError(905)
    if UserStates(user.state_id) == UserStates.not_confirmed:
        raise APIError(907)
    if UserStates(user.state_id) == UserStates.blocked:
        raise APIError(906)
    if UserStates(user.state_id) == UserStates.deleted:
        raise APIError(904)
    # установка токенов
    tokens = schemas.Tokens(
        access_token=jwt.generate_access_token(user.id, user.username, user.role_id, user.state_id),
        refresh_token=jwt.generate_refresh_token(user.id, user.username, user.role_id, user.state_id)
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
    user = await repository.user.get_user(id=jwt.decode_refresh_token(current_tokens.refresh_token).id)

    if not (UserStates(user.state_id) == UserStates.active):
        raise APIError(906)

    new_payload = schemas.TokenPayload(
        id=user.id,
        username=user.username,
        state_id=user.state_id,
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
