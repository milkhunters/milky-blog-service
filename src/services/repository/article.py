import uuid

from sqlalchemy import select, text
from sqlalchemy.orm import subqueryload, joinedload

from src.models import tables
from .base import BaseRepository


class ArticleRepo(BaseRepository[tables.Article]):
    table = tables.Article

    async def add_tag(self, article_id: uuid.UUID, tag_id: uuid.UUID) -> None:
        obj = await self.table.get(id=article_id)
        obj.tags.add(tables.Tag.get(id=tag_id))
        await obj.save()

    async def search(
            self,
            query: str,
            fields: list[str],
            limit: int = 100,
            offset: int = 0,
            order_by: str = "created_at",
            **kwargs
    ):
        query = f"%{query}%"
        result = await self._session.execute(
            select(self.table).where(
                *[self.table.__getattribute__(field).ilike(query) for field in fields]
            ).filter_by(**kwargs).order_by(text(order_by)).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def get(self, **kwargs) -> tables.Article:
        return (await self._session.execute(select(self.table).filter_by(**kwargs).options(
            subqueryload(self.table.tags),
            joinedload(self.table.owner)
        ))).scalars().first()

    async def get_all(
            self,
            limit: int = 100,
            offset: int = 0,
            order_by: str = "id",
            **kwargs
    ) -> list[tables.Article]:
        result = await self._session.execute(
            select(self.table).filter_by(**kwargs).order_by(text(order_by)).options(
                subqueryload(self.table.tags),
                joinedload(self.table.owner)
            ).limit(limit).offset(offset))
        return result.scalars().all()
