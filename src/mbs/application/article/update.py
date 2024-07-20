from datetime import datetime
from typing import Protocol

from pydantic import BaseModel

import mbs.domain.exceptions as domain_exceptions
from mbs.application.common.article_gateway import ArticleReader, ArticleWriter, ArticleFile
from mbs.application.common.exceptions import NotFound, Unauthorized, Forbidden, InvalidData
from mbs.application.common.file_gateway import FileReader
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor
from mbs.domain.models import ArticleState, FileId, ArticleId, UserId, File
from mbs.domain.services.access import AccessService
from mbs.domain.services.article import ArticleService
from mbs.domain.services.validator import ValidatorService


class UpdateArticleDTO(BaseModel):
    id: ArticleId
    title: str
    content: str
    state: ArticleState
    poster: FileId | None
    tags: list[str]


class ArticleResult(BaseModel):
    id: ArticleId
    title: str
    poster: FileId | None
    views: int
    likes: int
    tags: list[str]
    state: ArticleState
    files: list[File]
    author_id: UserId

    created_at: datetime
    updated_at: datetime | None


class ArticleGateway(ArticleReader, ArticleWriter, ArticleFile, Protocol):
    pass


class UpdateArticle(Interactor[UpdateArticleDTO, ArticleResult]):

    def __init__(
            self,
            article_gateway: ArticleGateway,
            article_service: ArticleService,
            file_reader: FileReader,
            access_service: AccessService,
            validator: ValidatorService,
            id_provider: IdProvider,
    ):
        self._article_gateway = article_gateway
        self._article_service = article_service
        self._file_reader = file_reader
        self._access_service = access_service
        self._validator = validator
        self._id_provider = id_provider

    async def __call__(self, data: UpdateArticleDTO) -> ArticleResult:
        article, files = await self._article_gateway.get_article_with_files(data.id)
        if not article:
            raise NotFound("Публикация не найдена")

        try:
            self._access_service.ensure_can_update_article(
                is_auth=self._id_provider.is_auth(),
                user_state=self._id_provider.user_state(),
                permissions=self._id_provider.permissions(),
                user_id=self._id_provider.user_id(),
                article_author_id=article.author_id,
                article_state=article.state,
            )
        except domain_exceptions.AccessDenied as error:
            raise Forbidden(str(error))
        except domain_exceptions.AuthenticationError as error:
            raise Unauthorized(str(error))

        validator_err_map: dict[str, str] = dict()
        try:
            self._validator.validate_article_title(data.title)
        except domain_exceptions.ValidationError as error:
            validator_err_map["title"] = str(error)

        try:
            self._validator.validate_article_content(data.content)
        except domain_exceptions.ValidationError as error:
            validator_err_map["content"] = str(error)

        try:
            for tag in data.tags:
                self._validator.validate_tag_title(tag)
        except domain_exceptions.ValidationError as error:
            validator_err_map["tags"] = str(error)

        if validator_err_map:
            raise InvalidData(validator_err_map)

        if data.poster and article.poster != data.poster:
            file = await self._file_reader.get_file(data.poster)
            if not file:
                raise InvalidData({"poster": "Файл не найден"})

            if not file.is_uploaded:
                raise InvalidData({"poster": "Файл не загружен"})

            is_linked = await self._article_gateway.is_file_linked_to_article(data.poster, data.id)
            if not is_linked:
                await self._article_gateway.link_file_to_article(data.poster, data.id)

        updated_article = self._article_service.update_article(
            article,
            title=data.title,
            content=data.content,
            state=data.state,
            poster=data.poster,
            views=article.views,
            tags=data.tags,
        )

        await self._article_gateway.save_article(updated_article)

        return ArticleResult(
            id=updated_article.id,
            title=updated_article.title,
            poster=updated_article.poster,
            views=updated_article.views,
            likes=updated_article.likes,
            tags=updated_article.tags,
            state=updated_article.state,
            files=files,
            author_id=updated_article.author_id,
            created_at=updated_article.created_at,
            updated_at=updated_article.updated_at,
        )
