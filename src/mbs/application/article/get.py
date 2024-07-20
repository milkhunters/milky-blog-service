from datetime import datetime
from typing import Protocol

from pydantic import BaseModel

from mbs.adapters.database.models import File
from mbs.application.common.article_gateway import ArticleReader, ArticleWriter, ArticleRater
from mbs.application.common.exceptions import NotFound, Forbidden, Unauthorized
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor

import mbs.domain.exceptions as domain_exceptions
from mbs.application.common.storage_gateway import StorageAccessLinkMaker
from mbs.application.common.tag_gateway import TagReader
from mbs.domain.models import ArticleState, ArticleId, FileId, UserId
from mbs.domain.services.access import AccessService
from mbs.domain.services.article import ArticleService


class ArticleResult(BaseModel):
    id: ArticleId
    title: str
    content: str
    poster: FileId | None
    views: int
    likes: int
    tags: list[str]
    is_rated: bool
    state: ArticleState
    files: list['FileItem']
    author_id: UserId

    created_at: datetime
    updated_at: datetime | None


class FileItem(BaseModel):
    id: FileId
    url: str
    filename: str
    content_type: str
    created_at: datetime


class ArticleGateway(ArticleReader, ArticleWriter, ArticleRater, Protocol):
    pass


class GetArticle(Interactor[ArticleId, ArticleResult]):

    def __init__(
            self,
            article_gateway: ArticleGateway,
            article_service: ArticleService,
            storage_access_link_maker: StorageAccessLinkMaker,
            tag_reader: TagReader,
            access_service: AccessService,
            id_provider: IdProvider,
    ):
        self._article_gateway = article_gateway
        self._article_service = article_service
        self._storage_access_link_maker = storage_access_link_maker
        self._tag_reader = tag_reader
        self._access_service = access_service
        self._id_provider = id_provider

    async def __call__(self, data: ArticleId) -> ArticleResult:
        article, files = await self._article_gateway.get_article_with_files(data)
        if not article:
            raise NotFound("Публикация не найдена")

        try:
            self._access_service.ensure_can_get_article(
                is_auth=self._id_provider.is_auth(),
                user_id=self._id_provider.user_id(),
                article_author_id=article.owner_id,
                permissions=self._id_provider.permissions(),
                user_state=self._id_provider.user_state(),
                article_state=article.state,
            )
        except domain_exceptions.AuthenticationError as error:
            raise Unauthorized(str(error))
        except domain_exceptions.AccessDenied as error:
            raise Forbidden(str(error))

        updated_article = self._article_service.update_article(
            article,
            title=article.title,
            content=article.content,
            state=article.state,
            views=article.views + 1,  # Could there be problems due to a non-atomic operation? 🤔
            poster=article.poster_id,
            tags=article.tags,
        )

        # todo gather
        await self._article_gateway.save_article(updated_article)
        is_rated = await self._article_gateway.is_article_rated(article.id, self._id_provider.user_id())

        return ArticleResult(
            id=article.id,
            title=article.title,
            content=article.content,
            poster=article.poster_id,
            views=article.views,
            likes=article.likes,
            tags=article.tags,
            is_rated=is_rated,
            state=article.state,
            files=[
                FileItem(
                    id=file.id,
                    url=await self._storage_access_link_maker.make_article_download_link(  # todo gather
                        article_id=article.id,
                        file_id=file.id
                    ),
                    filename=file.filename,
                    content_type=file.content_type,
                    created_at=file.created_at
                ) for file in files
            ],
            author_id=article.author_id,
            created_at=article.created_at,
            updated_at=article.updated_at,
        )
