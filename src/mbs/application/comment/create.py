from datetime import datetime
from typing import Protocol

from pydantic import BaseModel

from mbs.application.common.article_gateway import ArticleReader
from mbs.application.common.comment_gateway import CommentWriter, CommentReader
from mbs.application.common.exceptions import NotFound, Forbidden, Unauthorized, InvalidData
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor
from mbs.domain.models import CommentState, CommentId, UserId, ArticleId, ArticleState, File
from mbs.domain.services.access import AccessService
from mbs.domain.services.comment import CommentService
import mbs.domain.exceptions as domain_exceptions
from mbs.domain.services.validator import ValidatorService


class CreateCommentDTO(BaseModel):
    article_id: ArticleId
    content: str
    parent_id: CommentId | None


class CommentResult(BaseModel):
    id: CommentId
    content: str
    author_id: UserId
    article_id: ArticleId
    parent_id: CommentId | None
    is_rated: bool
    state: CommentState
    files: list[File]

    created_at: datetime
    updated_at: datetime | None


class CommentGateway(CommentReader, CommentWriter, Protocol):
    pass


class CreateComment(Interactor[CreateCommentDTO, CommentResult]):

    def __init__(
            self,
            comment_gateway: CommentGateway,
            comment_service: CommentService,
            article_reader: ArticleReader,
            access_service: AccessService,
            validator: ValidatorService,
            id_provider: IdProvider,
    ):
        self._comment_gateway = comment_gateway
        self._comment_service = comment_service
        self._article_reader = article_reader
        self._access_service = access_service
        self._validator = validator
        self._id_provider = id_provider

    async def __call__(self, data: CreateCommentDTO) -> CommentResult:
        article = await self._article_reader.get_article(data.article_id)
        if article is None:
            raise NotFound("Публикация не найдена")

        try:
            self._access_service.ensure_can_create_comment(
                is_auth=self._id_provider.is_auth(),
                user_state=self._id_provider.user_state(),
                permissions=self._id_provider.permissions(),
                article_state=ArticleState.PUBLISHED
            )
        except domain_exceptions.AuthenticationError as error:
            raise Unauthorized(str(error))
        except domain_exceptions.AccessDenied as error:
            raise Forbidden(str(error))

        validator_err_map: dict[str, str] = dict()
        try:
            self._validator.validate_comment_content(data.content)
        except domain_exceptions.ValidationError as error:
            validator_err_map["content"] = str(error)

        if validator_err_map:
            raise InvalidData(validator_err_map)

        if data.parent_id:
            parent = await self._comment_gateway.get_comment(data.parent_id)
            if parent is None:
                raise NotFound({"parent_id": "Комментарий не найден"})

            if parent.article_id != data.article_id:
                raise InvalidData({"parent_id": "Комментарий не принадлежит к данной публикации"})

            if parent.state == CommentState.DELETED:
                raise InvalidData({"parent_id": "Комментарий удален"})

        new_comment = self._comment_service.create_comment(
            content=data.content,
            author_id=self._id_provider.user_id(),
            article_id=data.article_id,
            parent_id=data.parent_id
        )

        await self._comment_gateway.save_comment(new_comment)

        return CommentResult(
            id=new_comment.id,
            content=new_comment.content,
            author_id=new_comment.author_id,
            article_id=new_comment.article_id,
            parent_id=new_comment.parent_id,
            is_rated=False,
            state=new_comment.state,
            files=[],
            created_at=new_comment.created_at,
            updated_at=new_comment.updated_at,
        )
