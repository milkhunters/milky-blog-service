import uuid

from src import exceptions
from src.services.repository import UserRepo
from src.services.auth.filters import role_filter, state_filter
from src.services.auth.password import verify_password

from src.models import schemas
from src.models.auth import BaseUser
from src.models.state import UserState
from src.models.role import Role, MainRole as M, AdditionalRole as A


class UserApplicationService:

    def __init__(self, current_user: BaseUser, *, user_repo: UserRepo):
        self._current_user = current_user
        self._repo = user_repo

    @role_filter(min_role=Role(M.USER, A.ONE))
    @state_filter(UserState.ACTIVE)
    async def get_me(self) -> schemas.User:
        user = await self._repo.get(id=self._current_user.id)
        return schemas.User.from_orm(user)

    @role_filter(min_role=Role(M.GUEST, A.ONE))
    async def get_user(self, user_id: uuid.UUID) -> schemas.UserSmall:
        user = await self._repo.get(id=user_id)

        if not user:
            raise exceptions.NotFound(f"Пользователь с id:{user_id} не найден!")

        return schemas.UserSmall.from_orm(user)

    @role_filter(min_role=Role(M.USER, A.ONE))
    @state_filter(UserState.ACTIVE)
    async def update_me(self, data: schemas.UserUpdate) -> None:
        await self._repo.update(
            id=self._current_user.id,
            **data.model_dump(exclude_unset=True)
        )

    @role_filter(min_role=Role(M.ADMIN, A.ONE))
    @state_filter(UserState.ACTIVE)
    async def update_user(self, user_id: uuid.UUID, data: schemas.UserUpdateByAdmin) -> None:
        user = await self._repo.get(id=user_id)
        if not user:
            raise exceptions.NotFound(f"Пользователь с id:{user_id} не найден!")

        await self._repo.update(
            id=user_id,
            **data.model_dump(exclude_unset=True)
        )

    @role_filter(min_role=Role(M.USER, A.ONE))
    @state_filter(UserState.ACTIVE)
    async def delete_me(self, password: str) -> None:
        user = await self._repo.get(id=self._current_user.id)
        if not verify_password(password, user.hashed_password):
            raise exceptions.BadRequest("Неверный пароль!")

        await self._repo.update(
            id=self._current_user.id,
            state=UserState.DELETED
        )
