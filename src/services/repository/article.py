from typing import List, Optional, Union
from tortoise.expressions import Q

from models import schemas
from src.models import tables
from .base import BaseRepo


class ArticleRepo:

    def __init__(self):
        self.table = tables.Article

    async def get(self, *args, **kwargs) -> Union[List[schemas.Article], schemas.Article, None]:
        pass

    async def insert(self, **kwargs) -> schemas.Article:
        return await self.table.create(**kwargs)

    async def update(self, article_id: int, **kwargs) -> None:
        await self.table.filter(id=article_id).update(**kwargs)

    async def delete(self, article_id: int) -> None:
        await self.table.filter(id=article_id).delete()


class CommentRepo(BaseRepo[tables.Comment, schemas.Comment]):
    # todo: проверить работоспособность и использовать для других repo
    pass
