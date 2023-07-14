from starlette.authentication import AuthCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.exceptions import ExceptionMiddleware

from fastapi.websockets import WebSocket
from fastapi.requests import Request
from fastapi.responses import Response

from src.models import schemas
from src.models.auth import AuthenticatedUser, UnauthenticatedUser
from src.services.auth import JWTManager
from src.services.auth import SessionManager
from src.services.repository import UserRepo


class MutableFlag:
    def __init__(self, value: bool = False):
        self._value = value

    def __bool__(self):
        return self._value

    def set(self, value: bool):
        self._value = value


class Container:
    def __init__(self, value):
        self._value = value

    def get(self):
        return self._value

    def set(self, value):
        self._value = value


async def jwt_pre_process(
        current_tokens: schemas.Tokens,
        jwt: JWTManager,
        session: SessionManager,
        session_id: str,
        db_session,
        req_obj: Request | WebSocket,
        is_auth: MutableFlag = MutableFlag(False),
        is_need_update: MutableFlag = MutableFlag(False),
        disable_update: bool = False,
):
    """
    Проверка авторизации и обновление токенов

    :param current_tokens: Текущие токены
    :param jwt: Менеджер JWT
    :param session: Менеджер сессий

    :param session_id: Идентификатор сессии
    :param db_session: Активная сессия БД
    :param req_obj: Объект запроса

    :param is_auth: Признак авторизации
    :param is_need_update: Признак необходимости обновления токенов
    :param disable_update: Признак принудительного отключения обновления токенов
    """
    # Проверка авторизации
    if current_tokens:
        is_valid_access_token = jwt.is_valid_access_token(current_tokens.access_token)
        is_valid_refresh_token = jwt.is_valid_refresh_token(current_tokens.refresh_token)
        is_valid_session = False

        if is_valid_refresh_token:
            # Проверка валидности сессии
            if await session.is_valid_session(session_id, current_tokens.refresh_token):
                is_valid_session = True

        is_auth.set(is_valid_access_token and is_valid_refresh_token and is_valid_session)
        is_need_update.set((not is_valid_access_token) and is_valid_refresh_token and is_valid_session)

    # Обновление токенов
    if is_need_update and not disable_update:
        user_id = jwt.decode_refresh_token(current_tokens.refresh_token).id
        async with db_session() as active_session:
            user = await UserRepo(active_session).get(id=user_id)

        if user:
            new_tokens = jwt.generate_tokens(
                id=user.id,
                username=user.username,
                role_id=user.role_id,
                state_id=user.state_id.value,
            )
            # Для бесшовного обновления токенов:
            req_obj.cookies["access_token"] = new_tokens.access_token
            req_obj.cookies["refresh_token"] = new_tokens.refresh_token

            current_tokens.access_token = new_tokens.access_token
            current_tokens.refresh_token = new_tokens.refresh_token

            is_auth.set(True)

    # Установка данных авторизации
    if is_auth:
        payload = jwt.decode_access_token(current_tokens.access_token)
        req_obj.scope["user"] = AuthenticatedUser(**payload.model_dump())
        req_obj.scope["auth"] = AuthCredentials(["authenticated"])
    else:
        req_obj.scope["user"] = UnauthenticatedUser()
        req_obj.scope["auth"] = AuthCredentials()


async def jwt_post_process(
        is_need_update: MutableFlag,
        response: Response,
        current_tokens: schemas.Tokens,
        jwt: JWTManager,
        session: SessionManager,
        session_id: str | int # todo
):
    if is_need_update:
        # Обновляем response
        jwt.set_jwt_cookie(response, current_tokens)
        await session.set_session_id(response, current_tokens.refresh_token, session_id)


class JWTMiddlewareWS:
    def __init__(self, app: ExceptionMiddleware):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "websocket":
            await self.app(scope, receive, send)
            return

        websocket = WebSocket(scope, receive=receive, send=send)
        jwt = JWTManager(config=websocket.app.state.config)
        session = SessionManager(
            redis_client=websocket.app.state.redis,
            debug=websocket.app.debug,
            config=websocket.app.state.config
        )
        db_session = websocket.app.state.db_session

        session_id = session.get_session_id(websocket)
        current_tokens = jwt.get_jwt_cookie(websocket)
        is_need_update = MutableFlag(False)
        is_auth = MutableFlag(False)

        # ----- pre_process -----
        # Проверка авторизации
        await jwt_pre_process(
            current_tokens=current_tokens,
            jwt=jwt,
            session=session,
            session_id=session_id,
            db_session=db_session,
            req_obj=websocket,
            is_need_update=is_need_update,
            is_auth=is_auth,
            disable_update=True
        )

        # ----- process -----
        await self.app(scope, receive, send)

        # ----- post_process -----
        pass


class JWTMiddlewareHTTP(BaseHTTPMiddleware):

    def __init__(self, app: ExceptionMiddleware):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        jwt = JWTManager(config=request.app.state.config)
        session = SessionManager(
            redis_client=request.app.state.redis,
            config=request.app.state.config
        )
        db_session = request.app.state.db_session

        # States
        session_id = session.get_session_id(request)
        current_tokens = jwt.get_jwt_cookie(request)
        is_need_update = MutableFlag(False)
        is_auth = MutableFlag(False)

        # ----- pre_process -----
        await jwt_pre_process(
            current_tokens=current_tokens,
            jwt=jwt,
            session=session,
            session_id=str(session_id),
            db_session=db_session,
            req_obj=request,
            is_need_update=is_need_update,
            is_auth=is_auth
        )

        response = await call_next(request)

        # ----- post_process -----
        await jwt_post_process(
            is_need_update=is_need_update,
            response=response,
            current_tokens=current_tokens,
            jwt=jwt,
            session=session,
            session_id=session_id
        )

        return response
