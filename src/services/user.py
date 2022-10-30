from models import schemas, UserStates
from models.role import Role, MainRole as M, AdditionalRole as A

import utils
from services.repository import UserRepo
from services.repository import DeletedUserRepo


class UserService(UserRepo):

    async def create(self, user: schemas.UserCreate) -> schemas.User:
        user = await self.insert(
            role_id=Role(M.user, A.one).value(),
            state_id=UserStates.active.value,  # TODO: сделать поле бд ENUM
            hashed_password=utils.get_hashed_password(user.password),
            username=user.username,
            email=user.email,
        )
        return user

    async def delete(self, user_id: int, dur=DeletedUserRepo()) -> None:
        await dur.insert(user_id)  # TODO: возможно, стоит сделать транзакцию; возможно, стоит разделить
        await self.update(user_id, state_id=UserStates.deleted.value)  # TODO: сделать поле бд ENUM
