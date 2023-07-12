from fastapi.requests import Request
from fastapi.responses import Response

from src.exceptions import AccessDenied, NotFound, AlreadyExists
from src.models import tables
from src.models.auth import BaseUser
from src.models import schemas
from src.models.enums.role import UserRole
from src.services.repository import UserRepo

from .jwt import JWTManager
from .session import SessionManager
from .filters import role_filter


class AuthApplicationService:
    def __init__(
            self,
            jwt: JWTManager,
            session: SessionManager,
            user_repo: UserRepo,
            current_user: BaseUser,
            debug: bool = False
    ):
        self._jwt = jwt
        self._session = session
        self._user_repo = user_repo
        self._current_user = current_user
        self._debug = debug

    @role_filter(UserRole.GUEST)
    async def create_user(self, user: schemas.UserSignUp) -> None:
        """
        Создание нового пользователя

        :param user: UserCreate

        :raise AccessDenied if user is already logged in
        :raise AlreadyExists Conflict if user already exists

        :return: User
        """

        if await self._user_repo.get_by_username_insensitive(user.username):
            raise AlreadyExists(f"Пользователь {user.username!r} уже существует")

        await self._user_repo.create(**user.dict())

    @role_filter(UserRole.GUEST)
    async def authenticate(self, username: str, hashed_password: str, response: Response) -> schemas.User:
        """
        Аутентификация пользователя

        PS: В качестве соли хеша используется
        имя пользователя

        TODO: Возможная оптимизация - искать пользователя по хешу пароля

        :param username:
        :param hashed_password:
        :param response:

        :return: User

        :raise AlreadyExists: if user is already logged in
        :raise NotFound: if user not found
        :raise AccessDenied: if user is banned
        """

        user: tables.User = await self._user_repo.get_by_username_insensitive(username=username)
        if not user:
            raise NotFound("Пользователь не найден")
        if hashed_password != user.hashed_password:
            raise NotFound("Неверная пара логин/пароль")
        if user.role == UserRole.BANNED:
            raise AccessDenied("Пользователь заблокирован")

        # генерация и установка токенов
        tokens = self._jwt.generate_tokens(user.id, user.username, user.role.value)
        self._jwt.set_jwt_cookie(response, tokens)  # todo менять подход
        await self._session.set_session_id(response, tokens.refresh_token)
        return schemas.User.from_orm(user)

    @role_filter(UserRole.USER)
    async def logout(self, request: Request, response: Response) -> None:
        """
        Выход пользователя
        :param request:
        :param response:
        :return:
        """
        self._jwt.delete_jwt_cookie(response)
        session_id = self._session.get_session_id(request)
        if session_id:
            await self._session.delete_session_id(session_id, response)

    @role_filter(UserRole.USER)
    async def refresh_tokens(self, request: Request, response: Response) -> None:
        """
        Обновление токенов
        :param request:
        :param response:

        :raise AccessDenied if session is invalid or user is banned
        :raise NotFound if user not found

        :return:
        """

        current_tokens = self._jwt.get_jwt_cookie(request)
        session_id = self._session.get_session_id(request)

        if not await self._session.is_valid_session(session_id, current_tokens.refresh_token):
            raise AccessDenied("Invalid session")

        user = await self._user_repo.get(id=self._jwt.decode_refresh_token(current_tokens.refresh_token).id)
        if not user:
            raise NotFound("User not found")

        if user.role == UserRole.BANNED:
            raise AccessDenied("User is banned")

        new_tokens = self._jwt.generate_tokens(user.id, user.username, user.role.value)
        self._jwt.set_jwt_cookie(response, new_tokens)
        # Для бесшовного обновления токенов:
        request.cookies["access_token"] = new_tokens.access_token
        request.cookies["refresh_token"] = new_tokens.refresh_token

        await self._session.set_session_id(response, new_tokens.refresh_token, session_id)
