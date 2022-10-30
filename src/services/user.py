from models import schemas, UserStates
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
        self._repo = user_repo
        self._du_repo = du_repo

    async def create(self, user: schemas.UserCreate) -> schemas.User:
        user = await self._repo.insert(
            role_id=Role(M.user, A.one).value(),
            state_id=UserStates.active.value,  # TODO: сделать поле бд ENUM
            hashed_password=utils.get_hashed_password(user.password),
            username=user.username,
            email=user.email,
        )
        return user

    async def delete(self, user_id: int) -> None:
        await self._du_repo.insert(user_id)  # TODO: возможно, стоит сделать транзакцию;
        await self._repo.update(user_id, state_id=UserStates.deleted.value)  # TODO: сделать поле бд ENUM
