from typing import TypeVar, Generic, List, Union


T = TypeVar('T')
S = TypeVar('S')


class BaseRepo(Generic[T, S]):
    def __init__(self):
        self.table = T

    async def get(self, *args, **kwargs) -> Union[List[S], S, None]:
        pass

    async def insert(self, **kwargs) -> S:
        return await self.table.create(**kwargs)

    async def update(self, id: int, **kwargs) -> None:
        await self.table.filter(id=id).update(**kwargs)

    async def delete(self, id: int) -> None:
        await self.table.filter(id=id).delete()
