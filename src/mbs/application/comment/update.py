from datetime import datetime
from typing import Protocol

from pydantic import BaseModel

from mbs.application.common.comment_gateway import CommentReader, CommentWriter, CommentRater
from mbs.application.common.exceptions import NotFound, Forbidden, Unauthorized, InvalidData
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor
from mbs.domain.models import CommentState, CommentId, UserId, ArticleId, File
from mbs.domain.services.access import AccessService
from mbs.domain.services.comment import CommentService
import mbs.domain.exceptions as domain_exceptions
from mbs.domain.services.validator import ValidatorService


class UpdateCommentDTO(BaseModel):
    id: CommentId
    content: str


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


class CommentGateway(CommentReader, CommentWriter, CommentRater, Protocol):
    pass


class UpdateComment(Interactor[UpdateCommentDTO, CommentResult]):

    def __init__(
            self,
            comment_gateway: CommentGateway,
            comment_service: CommentService,
            access_service: AccessService,
            validator: ValidatorService,
            id_provider: IdProvider,
    ):
        self._comment_gateway = comment_gateway
        self._comment_service = comment_service
        self._access_service = access_service
        self._validator = validator
        self._id_provider = id_provider

    async def __call__(self, data: UpdateCommentDTO) -> CommentResult:
        comment, files = await self._comment_gateway.get_comment_with_files(data.id)
        if comment is None:
            raise NotFound(f"Комментарий не найден")

        try:
            self._access_service.ensure_can_update_comment(
                is_auth=self._id_provider.is_auth(),
                user_id=self._id_provider.user_id(),
                user_state=self._id_provider.user_state(),
                comment_author_id=comment.author_id,
                comment_state=comment.state,
                permissions=self._id_provider.permissions(),
            )
        except domain_exceptions.AccessDenied as error:
            raise Forbidden(str(error))
        except domain_exceptions.AuthenticationError as error:
            raise Unauthorized(str(error))

        validator_err_map: dict[str, str] = dict()
        try:
            self._validator.validate_comment_content(data.content)
        except domain_exceptions.ValidationError as error:
            validator_err_map["content"] = str(error)

        if validator_err_map:
            raise InvalidData(validator_err_map)

        new_comment = self._comment_service.update_comment(
            comment=comment,
            content=data.content,
            state=comment.state,
        )

        # todo to gather
        await self._comment_gateway.save_comment(new_comment)
        is_rated = await self._comment_gateway.is_comment_rated(data.id, self._id_provider.user_id())

        return CommentResult(
            id=new_comment.id,
            content=new_comment.content,
            author_id=new_comment.author_id,
            article_id=new_comment.article_id,
            parent_id=new_comment.parent_id,
            is_rated=is_rated,
            state=new_comment.state,
            files=files,
            created_at=new_comment.created_at,
            updated_at=new_comment.updated_at,
        )
