from typing import Optional, Union

from exceptions import APIError
from models import schemas
from models.state import UserStates
from models.role import Role, MainRole as M, AdditionalRole as A

import utils
from services.repository import UserRepo
from services.repository import DeletedUserRepo


class UserService:

    def __init__(
            self,
            user_repo: UserRepo = UserRepo(),
            du_repo: DeletedUserRepo = DeletedUserRepo(),
    ):
        self._user_repo = user_repo
        self._du_repo = du_repo

    async def create_user(self, user: schemas.UserCreate) -> schemas.User:
        if await self.get_user(username=user.username):
            raise APIError(903)
        if await self.get_user(email=user.email):
            raise APIError(922)

        user = await self._user_repo.insert(
            role_id=Role(M.user, A.one).value(),
            state=UserStates.not_confirmed,
            hashed_password=utils.get_hashed_password(user.password),
            username=user.username,
            email=user.email,
        )
        return user

    async def get_user(self, user_id: int = None, username: str = None, email: str = None) -> Optional[schemas.User]:
        user = await self._user_repo.get(
            **{"id": user_id} if user_id else {"username__iexact": username} if username else {"email__iexact": email},
        )
        return schemas.User.from_orm(user) if user else None

    async def update_user(self, user_id: int, **kwargs) -> None:
        article = await self._user_repo.get(id=user_id)
        if not article:
            raise APIError(919)
        await self._user_repo.update(user_id, **kwargs)

    async def delete_user(self, user_id: int) -> None:
        await self._du_repo.insert(id=user_id)  # TODO: возможно, стоит сделать транзакцию;
        await self._user_repo.update(user_id, state=UserStates.deleted)
