from sqlalchemy import select, text, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import subqueryload

from mbs.adapters.database import models
from mbs.application.common.article_gateway import ArticleReader, ArticleWriter, ArticleRemover, ArticleRater
from mbs.domain.models import Article, ArticleId, ArticleState, UserId


class ArticleGateway(ArticleReader, ArticleWriter, ArticleRemover, ArticleRater):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_article(self, article_id: ArticleId) -> Article | None:
        stmt = select(models.Article).options(
            subqueryload(models.Article.tags),
            subqueryload(models.Article.likes)
        )

        if result := (await self._session.execute(stmt)).scalars().first():
            return Article(
                id=result.id,
                title=result.title,
                content=result.content,
                author_id=result.author_id,
                state=ArticleState(result.state),
                likes=len(result.likes),
                tags=[tag.title for tag in result.tags],
                created_at=result.created_at,
                updated_at=result.updated_at,
            )

    async def get_articles(
            self,
            limit: int,
            offset: int,
            order_by: str,
            state: ArticleState,
            tag: str = None,
            query: str = None,
            author_id: UserId = None,
    ) -> list[Article]:
        stmt = (
            select(
                models.Article,
                func.count(models.ArticleLike.author_id).label('likes')
            )
            .select_from(models.ArticleLike)
            .join(models.ArticleLike.article)
            .options(subqueryload(models.Article.tags))
            .order_by(text(order_by))
            .group_by(models.Article)
            .limit(limit)
            .offset(offset)
        )

        if tag:
            stmt = stmt.where(models.Tag.title == tag)

        if author_id:
            stmt = stmt.where(models.Article.author_id == author_id)

        if query:
            stmt = stmt.where(
                or_(*[getattr(models.Article, field).ilike(f"%{query}%") for field in ['title', 'content']])
            )

        result = await self._session.execute(stmt)
        articles = []
        for row in result:
            article = row[0]
            likes = row[1]
            article.likes = likes if likes else 0

            articles.append(Article(
                id=article.id,
                title=article.title,
                content=article.content,
                author_id=article.author_id,
                state=ArticleState(article.state),
                likes=article.likes,
                tags=[tag.title for tag in article.tags],
                created_at=article.created_at,
                updated_at=article.updated_at,
            ))

        return articles

    async def save_article(self, article: Article) -> None:
        async with self._session.begin() as transaction:
            stmt = select(models.Article).filter_by(id=article.id)
            model = (await self._session.execute(stmt)).scalars().first()

            if model:
                model.title = article.title
                model.content = article.content
                model.poster = article.poster
                model.state = article.state.value
                model.views = article.views
                model.author_id = article.author_id
                model.created_at = article.created_at
                model.updated_at = article.updated_at
            else:
                model = models.Article(
                    id=article.id,
                    title=article.title,
                    content=article.content,
                    poster=article.poster,
                    state=article.state.value,
                    views=article.views,
                    author_id=article.author_id,
                    created_at=article.created_at,
                    updated_at=article.updated_at,
                )
                transaction.session.add(model)

            existing_tags = (await self._session.execute(
                select(models.Tag).filter(models.Tag.title.in_([tag for tag in article.tags]))
            )).scalars().all()
            existing_tags_titles = {tag.title for tag in existing_tags}

            for tag_title in article.tags:
                if tag_title not in existing_tags_titles:
                    new_tag = models.Tag(title=tag_title)
                    self._session.add(new_tag)
                    model.tags.append(new_tag)
                else:
                    model.tags.append(next((t for t in existing_tags if t.title == tag_title), None))

            await transaction.commit()

    async def remove_article(self, article_id: ArticleId) -> None:
        async with self._session.begin() as transaction:
            stmt = select(models.Article).filter_by(id=article_id)
            if model := (await self._session.execute(stmt)).scalars().first():
                await transaction.session.delete(model)
            await transaction.commit()

    async def rate_article(self, article_id: ArticleId, user_id: UserId) -> None:
        async with self._session.begin() as transaction:
            stmt = select(models.ArticleLike).filter_by(article_id=article_id, author_id=user_id)
            if model := (await self._session.execute(stmt)).scalars().first():
                await transaction.session.delete(model)
            else:
                transaction.session.add(models.ArticleLike(article_id=article_id, author_id=user_id))
            await transaction.commit()

    async def is_articles_rated(self, article_ids: list[ArticleId], user_id: UserId) -> list[bool]:
        stmt = select(models.ArticleLike).filter(
            models.ArticleLike.article_id.in_(article_ids),
            models.ArticleLike.author_id == user_id
        )
        rated_ids = [row.article_id for row in (await self._session.execute(stmt)).scalars()]
        return [article_id in rated_ids for article_id in article_ids]

    async def is_article_rated(self, article_id: ArticleId, user_id: UserId) -> bool:
        stmt = select(models.ArticleLike).filter_by(article_id=article_id, author_id=user_id)
        return bool((await self._session.execute(stmt)).scalars().first())
