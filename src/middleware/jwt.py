from starlette.authentication import AuthCredentials, UnauthenticatedUser, BaseUser
from starlette.middleware.base import BaseHTTPMiddleware

from fastapi.responses import Response
from fastapi.requests import Request

from models import schemas, Role
from models.state import UserStates
from services.auth import JWTManager
from services.auth import SessionManager
from services.user import UserService


class JWTMiddleware(BaseHTTPMiddleware):

    def __init__(
            self,
            app,
            jwt: JWTManager = JWTManager(),
            session: SessionManager = SessionManager(),
    ):
        super().__init__(app)

        self.jwt = jwt
        self.session = session
        self.user_service = UserService()

    async def dispatch(self, request: Request, call_next):
        session_id = self.session.get_session_id(request)
        current_tokens = self.jwt.get_jwt_cookie(request)
        is_need_update = False
        is_auth = False

        # ----- pre_process -----
        # Проверка авторизации
        if current_tokens:
            is_valid_access_token = self.jwt.is_valid_access_token(current_tokens.access_token)
            is_valid_refresh_token = self.jwt.is_valid_refresh_token(current_tokens.refresh_token)
            is_valid_session = False

            if is_valid_refresh_token:
                # Проверка валидности сессии
                if await self.session.is_valid_session(session_id, current_tokens.refresh_token):
                    is_valid_session = True

            is_auth = is_valid_access_token and is_valid_refresh_token and is_valid_session
            is_need_update = (not is_valid_access_token) and is_valid_refresh_token and is_valid_session

        # Обновление токенов
        if is_need_update:
            user_id = self.jwt.decode_refresh_token(current_tokens.refresh_token).id
            user = await self.user_service.get_user(user_id=user_id)
            if user:
                new_payload = schemas.TokenPayload(
                    id=user.id,
                    username=user.username,
                    role_id=user.role_id,
                    state_id=user.state.value,
                    exp=0
                )  # exp не используется, но нужно для составления модели
                new_tokens = schemas.Tokens(
                    access_token=self.jwt.generate_access_token(**new_payload.dict()),
                    refresh_token=self.jwt.generate_refresh_token(**new_payload.dict())
                )
                # Для бесшовного обновления токенов:
                request.cookies["access_token"] = new_tokens.access_token
                request.cookies["refresh_token"] = new_tokens.refresh_token
                current_tokens = new_tokens
                is_auth = True

        # Установка данных авторизации
        if is_auth:
            payload: schemas.TokenPayload = self.jwt.decode_access_token(current_tokens.access_token)
            request.scope["user"] = AuthenticatedUser(**payload.dict())
            request.scope["auth"] = AuthCredentials(["authenticated"])
        else:
            request.scope["user"] = UnauthenticatedUser()
            request.scope["auth"] = AuthCredentials()

        response = await call_next(request)

        # ----- post_process -----
        if is_need_update:
            # Обновляем response
            self.jwt.set_jwt_cookie(response, current_tokens)
            await self.session.set_session_id(response, current_tokens.refresh_token, session_id)

        return response


class AuthenticatedUser(BaseUser):
    def __init__(self, id: int, username: str, role_id: int, state_id: int, **kwargs):
        self.id = id
        self.username = username
        self.role_id = role_id
        self.state_id = state_id

    def is_authenticated(self) -> bool:
        return True

    def display_name(self) -> str:
        return self.username

    def identity(self) -> int:
        return self.id

    def role(self) -> Role:
        return Role.from_int(self.role_id)

    def state(self) -> UserStates:
        return UserStates(self.state_id)

    def __eq__(self, other):
        return isinstance(other, AuthenticatedUser) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"<AuthenticatedUser(id={self.id}, username={self.username})>"
