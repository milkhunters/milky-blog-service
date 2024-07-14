from datetime import datetime
from typing import Protocol

from pydantic import BaseModel

import mbs.domain.exceptions as domain_exceptions
from mbs.application.common.article_gateway import ArticleWriter
from mbs.application.common.exceptions import Unauthorized, InvalidData, Forbidden
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor
from mbs.application.common.tag_gateway import TagReader, TagLinker, TagWriter
from mbs.domain.models import ArticleState, ArticleId, FileId, UserId
from mbs.domain.services.access import AccessService
from mbs.domain.services.article import ArticleService
from mbs.domain.services.tag import TagService
from mbs.domain.services.validator import ValidatorService


class CreateArticleDTO(BaseModel):
    title: str
    content: str
    state: ArticleState
    tags: list[str]


class CreateArticleResult(BaseModel):
    id: ArticleId
    title: str
    content: str
    poster: FileId | None
    views: int
    likes: int
    tags: list[str]
    state: ArticleState
    author_id: UserId

    created_at: datetime
    updated_at: datetime | None


class TagGateway(TagReader, TagWriter, TagLinker, Protocol):
    pass


class CreateArticle(Interactor[CreateArticleDTO, CreateArticleResult]):

    def __init__(
            self,
            article_writer: ArticleWriter,
            access_service: AccessService,
            article_service: ArticleService,
            tag_gateway: TagGateway,
            tag_service: TagService,
            validator: ValidatorService,
            id_provider: IdProvider,
    ):
        self._article_writer = article_writer
        self._access_service = access_service
        self._article_service = article_service
        self._tag_gateway = tag_gateway
        self._tag_service = tag_service
        self._validator = validator
        self._id_provider = id_provider

    async def __call__(self, data: CreateArticleDTO) -> CreateArticleResult:

        try:
            self._access_service.ensure_can_create_article(
                is_auth=self._id_provider.is_auth(),
                permissions=self._id_provider.permissions(),
                user_state=self._id_provider.user_state(),
            )
        except domain_exceptions.AuthenticationError as error:
            raise Unauthorized(str(error))
        except domain_exceptions.AccessDenied as error:
            raise Forbidden(str(error))

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

        article = self._article_service.create_article(
            title=data.title,
            content=data.content,
            state=data.state,
            author_id=self._id_provider.user_id(),
            tags=data.tags
        )
        await self._article_writer.save_article(article)

        return CreateArticleResult(
            id=article.id,
            title=article.title,
            content=article.content,
            poster=article.poster,
            views=article.views,
            likes=article.likes,
            tags=article.tags,
            state=article.state,
            author_id=article.author_id,
            created_at=article.created_at,
            updated_at=article.updated_at
        )
