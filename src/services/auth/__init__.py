import time
from random import randint

from fastapi.requests import Request
from fastapi.responses import Response

from src import exceptions
from src.models import tables
from src.models import schemas
from src.models.auth import BaseUser
from src.models.state import UserState
from src.models.role import Role, MainRole as M, AdditionalRole as A, RoleRange
from src.services.repository import UserRepo

from .jwt import JWTManager
from .password import verify_password, get_hashed_password
from .session import SessionManager
from .filters import role_filter

from src.services.email import EmailService
from src.utils import RedisClient
from src.utils.validators import is_valid_email


class AuthApplicationService:
    def __init__(
            self,
            current_user: BaseUser,
            *,
            jwt_manager: JWTManager,
            session_manager: SessionManager,
            user_repo: UserRepo,
            redis_client: RedisClient,
            email_service: EmailService,
    ):
        self._current_user = current_user
        self._jwt_manager = jwt_manager
        self._session_manager = session_manager
        self._user_repo = user_repo
        self._redis_client = redis_client
        self._email_service = email_service

    @role_filter(Role(M.GUEST, A.ONE))
    async def create_user(self, user: schemas.UserCreate) -> None:
        """
        Создание нового пользователя

        :param user: UserCreate

        :raise AccessDenied if user is already logged in
        :raise AlreadyExists Conflict if user already exists

        :return: User
        """

        if await self._user_repo.get_by_username_insensitive(user.username):
            raise exceptions.AlreadyExists(f"Пользователь {user.username!r} уже существует")

        if await self._user_repo.get_by_email_insensitive(user.email):
            raise exceptions.AlreadyExists(f"Пользователь с email {user.email!r} уже существует")

        hashed_password = get_hashed_password(user.password)
        await self._user_repo.create(**user.model_dump(exclude={"password"}), hashed_password=hashed_password)

    @role_filter(Role(M.GUEST, A.ONE))
    async def authenticate(self, data: schemas.UserAuth, response: Response) -> schemas.User:
        """
        Аутентификация пользователя

        :param data: UserAuth
        :param response: Response

        :return: User

        :raise AlreadyExists: if user is already logged in
        :raise NotFound: if user not found
        :raise AccessDenied: if user is banned
        """

        user: tables.User = await self._user_repo.get_by_username_insensitive(username=data.username)
        if not user:
            raise exceptions.NotFound("Пользователь не найден")
        if not verify_password(data.password, user.hashed_password):
            raise exceptions.NotFound("Неверная пара логин/пароль")
        if user.state == UserState.BLOCKED:
            raise exceptions.AccessDenied("Пользователь заблокирован")

        # Генерация и установка токенов
        tokens = self._jwt_manager.generate_tokens(str(user.id), user.username, user.role_id, user.state.value)
        self._jwt_manager.set_jwt_cookie(response, tokens)
        await self._session_manager.set_session_id(response, tokens.refresh_token)
        return schemas.User.model_validate(user)

    @role_filter(Role(M.GUEST, A.ONE))
    async def send_verify_code(self, email: str) -> None:
        """
        Отправка кода подтверждения на почту

        :param email:

        :raise NotFound: if user not found
        :raise AccessDenied: if user is banned
        """

        user: tables.User = await self._user_repo.get(email=email)
        if not user:
            raise exceptions.NotFound("Пользователь не найден")

        user: tables.User = await self._user_repo.get(email=email)
        if not user:
            raise exceptions.NotFound("Пользователь не найден")
        if user.state != UserState.NOT_CONFIRMED:
            raise exceptions.AccessDenied("Пользователь уже подтвержден")

        keys = await self._redis_client.keys(pattern=f'{email}*')
        if keys:
            data_key = keys[0].split(':')
            if int(data_key[1]) > int(time.time()) - 120:
                raise exceptions.BadRequest("Код уже отправлен")
            await self._redis_client.delete(keys[0])

        code = randint(100000, 999999)
        await self._redis_client.set(f"""{email}:{int(time.time())}:0""", code, expire=60 * 60)
        await self._email_service.send_mail(email, "Подтверждение почты", f"Код подтверждения: {code}")

    @role_filter(Role(M.GUEST, A.ONE))
    async def verify_email(self, email: str, code: int) -> None:
        """
        Подтверждение почты

        :param email:
        :param code:

        :raise NotFound: if user not found
        :raise AccessDenied: if user is banned
        """

        if not is_valid_email(email):
            raise exceptions.BadRequest("Неверный формат почты")

        user: tables.User = await self._user_repo.get(email=email)
        if not user:
            raise exceptions.NotFound("Пользователь не найден")
        if user.state != UserState.NOT_CONFIRMED:
            raise exceptions.AccessDenied("Пользователь уже подтвержден")

        keys = await self._redis_client.keys(pattern=f'{email}*')
        if not keys:
            raise exceptions.BadRequest("Код не отправлен")

        data = keys[0].split(':')
        email = data[0]
        timestamp = int(data[1])
        attempts = int(data[2])

        if timestamp < int(time.time()) - 86400:
            raise exceptions.BadRequest("Код устарел, отправьте новый")

        if attempts > 3:
            raise exceptions.BadRequest("Превышено количество попыток")

        code_in_db = await self._redis_client.get(keys[0])
        if int(code_in_db) != code:
            await self._redis_client.delete(keys[0])
            await self._redis_client.set(f"{email}:{timestamp}:{attempts + 1}", code, expire=60 * 60)
            raise exceptions.BadRequest("Неверный код")

        await self._user_repo.update(user.id, state=UserState.ACTIVE)
        await self._redis_client.delete(keys[0])

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

        if user.state == UserState.BLOCKED:
            raise exceptions.AccessDenied("Пользователь заблокирован")

        new_tokens = self._jwt_manager.generate_tokens(str(user.id), user.username, user.role_id, user.state.value)
        self._jwt_manager.set_jwt_cookie(response, new_tokens)
        # Для бесшовного обновления токенов:
        request.cookies["access_token"] = new_tokens.access_token
        request.cookies["refresh_token"] = new_tokens.refresh_token

        await self._session_manager.set_session_id(response, new_tokens.refresh_token, session_id)
