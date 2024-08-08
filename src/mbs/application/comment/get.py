from datetime import datetime
from typing import Protocol

from pydantic import BaseModel

from mbs.application.common.comment_gateway import CommentReader, CommentRater
from mbs.application.common.exceptions import NotFound, Forbidden, Unauthorized
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor
from mbs.domain.models import CommentState, CommentId, UserId, ArticleId, File
from mbs.domain.services.access import AccessService
import mbs.domain.exceptions as domain_exceptions


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


class CommentGateway(CommentReader, CommentRater, Protocol):
    pass


class GetComment(Interactor[CommentId, CommentResult]):

    def __init__(
            self,
            comment_gateway: CommentGateway,
            access_service: AccessService,
            id_provider: IdProvider,
    ):
        self._comment_gateway = comment_gateway
        self._access_service = access_service
        self._id_provider = id_provider

    async def __call__(self, data: CommentId) -> CommentResult:
        comment, files = await self._comment_gateway.get_comment_with_files(data)
        if comment is None:
            raise NotFound(f"Комментарий не найден")

        try:
            self._access_service.ensure_can_get_published_comment(
                permissions=self._id_provider.permissions(),
            )
        except domain_exceptions.AccessDenied as error:
            raise Forbidden(str(error))

        if comment.state != CommentState.PUBLISHED:
            try:
                self._access_service.ensure_can_get_comment(
                    is_auth=self._id_provider.is_auth(),
                    user_state=self._id_provider.user_state(),
                    permissions=self._id_provider.permissions(),
                )
            except domain_exceptions.AccessDenied as error:
                raise Forbidden(str(error))
            except domain_exceptions.AuthenticationError as error:
                raise Unauthorized(str(error))

        is_rated = await self._comment_gateway.is_comment_rated(data, self._id_provider.user_id())

        return CommentResult(
            id=comment.id,
            content=comment.content,
            author_id=comment.author_id,
            article_id=comment.article_id,
            parent_id=comment.parent_id,
            is_rated=is_rated,
            state=comment.state,
            files=files,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )
