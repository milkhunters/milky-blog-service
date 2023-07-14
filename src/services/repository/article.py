import uuid

from sqlalchemy import select, text

from src.models import tables
from .base import BaseRepository


class ArticleRepo(BaseRepository[tables.Article]):
    table = tables.Article

    async def add_tag(self, article_id: uuid.UUID, tag_id: uuid.UUID) -> None:
        """
        Добавляет запись в m2m колонку связи.

        TODO: вынести в сервис

        """
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

    async def get_full_article(self, id: uuid.UUID):
        result = await self.session.execute(
            select(self.table).where(
                self.table.id == id
            ).join(
                tables.Article.tags
            ).join(
                tables.Article.owner
            )
        )
        return result.scalars().first()
