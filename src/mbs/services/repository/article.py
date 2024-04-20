import uuid

from sqlalchemy import select, text, func, or_, and_
from sqlalchemy.orm import subqueryload

from mbs.models import tables
from .base import BaseRepository
from ...models.tables import Like


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
    ) -> list[tables.Article]:
        return await self.__get_range(
            query=query,
            fields=fields,
            limit=limit,
            offset=offset,
            order_by=order_by,
            **kwargs
        )

    async def get_all(
            self, limit: int = 100,
            offset: int = 0,
            order_by: str = "id",
            **kwargs
    ) -> list[tables.Article]:
        return await self.__get_range(
            limit=limit,
            offset=offset,
            order_by=order_by,
            **kwargs
        )

    async def get(self, **kwargs) -> tables.Article:
        stmt = select(self.table).filter_by(**kwargs).options(subqueryload(self.table.tags))
        return (await self._session.execute(stmt)).scalars().first()

    async def __get_range(
            self,
            *,
            query: str = None,
            fields: list[str] = None,
            limit: int = 100,
            offset: int = 0,
            order_by: str = "id",
            **kwargs
    ) -> list[tables.Article]:
        # Лайки
        subquery = (
            select(
                Like.article_id,
                func.count(Like.id).label('likes_count')
            )
            .group_by(Like.article_id)
            .subquery()
        )

        # Основной запрос
        stmt = (
            select(
                self.table,
                subquery.c.likes_count
            )
            .outerjoin(subquery, self.table.id == subquery.c.article_id)
            .options(subqueryload(self.table.tags))
            .order_by(text(order_by))
            .limit(limit)
            .offset(offset)
        )

        # Фильтры kwargs
        stmt = stmt.where(
            and_(*[getattr(self.table, field) == value for field, value in kwargs.items()])
        )

        # Поиск
        if query and fields:
            stmt = stmt.where(
                or_(*[getattr(self.table, field).ilike(f"%{query}%") for field in fields])
            )

        result = await self._session.execute(stmt)
        articles_with_likes = []
        for row in result:
            article = row[0]
            likes_count = row[1]
            article.likes_count = likes_count if likes_count else 0
            articles_with_likes.append(article)

        return articles_with_likes
