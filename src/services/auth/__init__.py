from fastapi.requests import Request
from fastapi.responses import Response

from src import exceptions
from src.models import tables
from src.models import schemas
from src.models.auth import BaseUser
from src.models.state import UserStates
from src.models.role import Role, MainRole as M, AdditionalRole as A, RoleRange
from src.services.repository import UserRepo

from .jwt import JWTManager
from .password import verify_password
from .session import SessionManager
from .filters import role_filter


class AuthApplicationService:
    def __init__(
            self,
            current_user: BaseUser,
            *,
            jwt_manager: JWTManager,
            session_manager: SessionManager,
            user_repo: UserRepo,
    ):
        self._current_user = current_user
        self._jwt_manager = jwt_manager
        self._session_manager = session_manager
        self._user_repo = user_repo

    @role_filter(Role(M.GUEST, A.ONE))
    async def create_user(self, user: schemas.UserCreate) -> schemas.User:
        """
        Создание нового пользователя

        :param user: UserCreate

        :raise AccessDenied if user is already logged in
        :raise AlreadyExists Conflict if user already exists

        :return: User
        """

        if await self._user_repo.get_by_username_insensitive(user.username):
            raise exceptions.AlreadyExists(f"Пользователь {user.username!r} уже существует")

        user = await self._user_repo.create(**user.model_dump())
        return schemas.User.from_orm(user)

    @role_filter(Role(M.GUEST, A.ONE))
    async def authenticate(self, username: str, password: str, response: Response) -> schemas.User:
        """
        Аутентификация пользователя

        :param username:
        :param password:
        :param response:

        :return: User

        :raise AlreadyExists: if user is already logged in
        :raise NotFound: if user not found
        :raise AccessDenied: if user is banned
        """

        user: tables.User = await self._user_repo.get_by_username_insensitive(username=username)
        if not user:
            raise exceptions.NotFound("Пользователь не найден")
        if not verify_password(password, user.hashed_password):
            raise exceptions.NotFound("Неверная пара логин/пароль")
        if user.state == UserStates.BLOCKED:
            raise exceptions.AccessDenied("Пользователь заблокирован")

        # Генерация и установка токенов
        tokens = self._jwt_manager.generate_tokens(user.id, user.username, user.role.value)
        self._jwt_manager.set_jwt_cookie(response, tokens)
        await self._session_manager.set_session_id(response, tokens.refresh_token)
        return schemas.User.from_orm(user)

    @role_filter(RoleRange("*"), exclude=[Role(M.GUEST, A.ONE)])
    async def logout(self, request: Request, response: Response) -> None:
        self._jwt_manager.delete_jwt_cookie(response)
        session_id = self._session_manager.get_session_id(request)
        if session_id:
            await self._session_manager.delete_session_id(session_id, response)

    @role_filter(RoleRange("*"), exclude=[Role(M.GUEST, A.ONE)])
    async def refresh_tokens(self, request: Request, response: Response) -> None:
        """
        Обновление токенов
        :param request:
        :param response:

        :raise AccessDenied if session is invalid or user is banned
        :raise NotFound if user not found

        :return:
        """

        current_tokens = self._jwt_manager.get_jwt_cookie(request)
        session_id = self._session_manager.get_session_id(request)

        if not await self._session_manager.is_valid_session(session_id, current_tokens.refresh_token):
            raise exceptions.AccessDenied("Invalid session")

        user = await self._user_repo.get(id=self._jwt_manager.decode_refresh_token(current_tokens.refresh_token).id)
        if not user:
            raise exceptions.NotFound("Пользователь не найден")

        if user.state == UserStates.BLOCKED:
            raise exceptions.AccessDenied("Пользователь заблокирован")

        new_tokens = self._jwt_manager.generate_tokens(user.id, user.username, user.role.value)
        self._jwt_manager.set_jwt_cookie(response, new_tokens)
        # Для бесшовного обновления токенов:
        request.cookies["access_token"] = new_tokens.access_token
        request.cookies["refresh_token"] = new_tokens.refresh_token

        await self._session_manager.set_session_id(response, new_tokens.refresh_token, session_id)
