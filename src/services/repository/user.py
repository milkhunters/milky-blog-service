from typing import List, Optional, Union
from tortoise.expressions import Q

from models import schemas
from src.models import tables


class UserRepo:
    def __init__(self):
        self.table = tables.User

    async def get(self, *args, **kwargs) -> Union[List[schemas.User], schemas.User, None]:
        pass

    async def insert(self, **kwargs) -> schemas.User:
        return await self.table.create(**kwargs)

    async def update(self, user_id: int, **kwargs) -> None:
        await self.table.filter(id=user_id).update(**kwargs)

    async def delete(self, user_id: int) -> None:
        await self.table.filter(id=user_id).delete()


class DeletedUserRepo:
    def __init__(self):
        self.table = tables.UserDeleted

    async def get(self) -> Union[List[tables.UserDeleted], tables.UserDeleted, None]:
        pass

    async def insert(self, user_id: int) -> tables.UserDeleted:  # Todo: изменить возвращаемый тип на схему
        return await self.table.create(id=user_id)

    async def delete(self, user_id: int) -> None:
        await self.table.filter(id=user_id).delete()
