import textwrap
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from mbs.application.common.article_gateway import ArticleReader
from mbs.application.common.exceptions import Forbidden, Unauthorized
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor
from mbs.domain.models import ArticleState, UserId, ArticleId, FileId
from mbs.domain.services.access import AccessService
import mbs.domain.exceptions as domain_exceptions


class GetArticleRangeDTO(BaseModel):
    page: int
    per_page: int
    order_by: Literal["title", "updated_at", "created_at"] = "created_at"
    query: str | None
    state: ArticleState = ArticleState.PUBLISHED
    author_id: UserId | None


class ArticleItem(BaseModel):
    id: ArticleId
    title: str
    description: str
    poster: FileId | None
    views: int
    likes: int
    tags: list[str]
    state: ArticleState
    author_id: UserId

    created_at: datetime
    updated_at: datetime | None


class GetArticleRange(Interactor[GetArticleRangeDTO, list[ArticleItem]]):

    def __init__(
            self,
            article_reader: ArticleReader,
            access_service: AccessService,
            id_provider: IdProvider,
    ):
        self._article_reader = article_reader
        self._access_service = access_service
        self._id_provider = id_provider

    async def __call__(self, data: GetArticleRangeDTO) -> list[ArticleItem]:
        try:
            self._access_service.ensure_can_get_article(
                is_auth=self._id_provider.is_auth(),
                user_id=self._id_provider.user_id(),
                article_author_id=data.author_id,
                permissions=self._id_provider.permissions(),
                user_state=self._id_provider.user_state(),
                article_state=data.state,
            )
        except domain_exceptions.AuthenticationError as error:
            raise Unauthorized(str(error))
        except domain_exceptions.AccessDenied as error:
            raise Forbidden(str(error))

        articles = await self._article_reader.get_articles(
            limit=data.per_page,
            offset=(data.page - 1) * data.per_page,
            order_by=data.order_by,
            query=data.query,
            state=data.state,
            author_id=data.author_id
        )

        return [
            ArticleItem(
                id=article.id,
                title=article.title,
                description=textwrap.shorten(article.content, width=150, placeholder="..."),
                poster=article.poster,
                views=article.views,
                likes=article.likes,
                tags=article.tags,
                state=article.state,
                author_id=article.owner_id,
                created_at=article.created_at,
                updated_at=article.updated_at,
            )
            for article in articles
        ]