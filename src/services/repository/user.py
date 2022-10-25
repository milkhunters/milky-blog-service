from typing import List, Optional
from tortoise.expressions import Q

from src.models import tables
from src.models import Role, A, M
from src.models import UserStates
from src.utils import get_hashed_password


async def get_user(*args, **kwargs) -> Optional[tables.User]:
    return await tables.User.filter(*args, **kwargs).first()


async def get_users(*args, **kwargs) -> Optional[List[tables.User]]:
    return await tables.User.filter(*args, **kwargs)


async def create_user(**kwargs) -> tables.User:
    return await tables.User.create(
        role_id=Role(M.user, A.one).value(),
        state_id=UserStates.active.value,
        hashed_password=get_hashed_password(kwargs.pop("password")),
        **kwargs
    )


async def update_user(user_id: int, **kwargs) -> tables.User:
    user = await tables.User.update_from_dict(await get_user(id=user_id), kwargs)
    await user.save()
    return user


async def delete(user_id: int) -> None:
    await update_user(user_id, state_id=UserStates.deleted.value)
    await tables.UserDeleted.create(id=user_id)