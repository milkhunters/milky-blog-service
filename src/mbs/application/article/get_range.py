import textwrap
from datetime import datetime
from typing import Literal, Protocol

from pydantic import BaseModel

import mbs.domain.exceptions as domain_exceptions
from mbs.application.common.article_gateway import ArticleReader, ArticleRater
from mbs.application.common.exceptions import Forbidden, Unauthorized
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor
from mbs.application.common.storage_gateway import StorageAccessLinkMaker
from mbs.domain.models import ArticleState, UserId, ArticleId
from mbs.domain.services.access import AccessService


class GetArticleRangeDTO(BaseModel):
    page: int
    per_page: int
    order_by: Literal["title", "updated_at", "created_at"] = "created_at"
    query: str | None
    tag: str | None
    state: ArticleState = ArticleState.PUBLISHED
    author_id: UserId | None


class ArticleItem(BaseModel):
    id: ArticleId
    title: str
    description: str
    poster_url: str | None
    views: int
    likes: int
    comments: int
    tags: list[str]
    is_rated: bool
    state: ArticleState
    author_id: UserId

    created_at: datetime
    updated_at: datetime | None


class ArticleGateway(ArticleReader, ArticleRater, Protocol):
    pass


class GetArticleRange(Interactor[GetArticleRangeDTO, list[ArticleItem]]):

    def __init__(
            self,
            article_gateway: ArticleGateway,
            storage_access_link_maker: StorageAccessLinkMaker,
            access_service: AccessService,
            id_provider: IdProvider,
    ):
        self._article_gateway = article_gateway
        self._storage_access_link_maker = storage_access_link_maker
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

        # todo: to gather
        articles = await self._article_gateway.get_articles_with_like_comment(
            limit=data.per_page,
            offset=(data.page - 1) * data.per_page,
            order_by=data.order_by,
            query=data.query,
            tag=data.tag,
            state=data.state,
            author_id=data.author_id
        )

        rated_states = await self._article_gateway.is_articles_rated(
            article_ids=[article.id for article in articles],
            user_id=self._id_provider.user_id()
        )

        # todo: to gather
        poster_urls = [
            await self._storage_access_link_maker.make_article_download_link(article.id, article.poster_id)
            if article.poster_id
            else None
            for article in articles
        ]

        return [
            ArticleItem(
                id=article.id,
                title=article.title,
                description=textwrap.shorten(article.content, width=150, placeholder="..."),
                poster_url=poster_url,
                views=article.views,
                likes=article.likes,
                comments=article.comments,
                tags=article.tags,
                is_rated=is_rated,
                state=article.state,
                author_id=article.owner_id,
                created_at=article.created_at,
                updated_at=article.updated_at,
            )
            for article, is_rated, poster_url in zip(articles, rated_states, poster_urls)
        ]
