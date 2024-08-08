from typing import Protocol

from mbs.application.common.comment_gateway import CommentReader, CommentWriter
from mbs.application.common.exceptions import NotFound, Forbidden, Unauthorized, InvalidData
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor
from mbs.domain.services.access import AccessService
from mbs.domain.models import CommentId, CommentState
import mbs.domain.exceptions as domain_exceptions
from mbs.domain.services.comment import CommentService


class CommentGateway(CommentReader, CommentWriter, Protocol):
    pass


class DeleteComment(Interactor[CommentId, None]):

    def __init__(
            self,
            comment_gateway: CommentGateway,
            comment_service: CommentService,
            access_service: AccessService,
            id_provider: IdProvider,
    ):
        self._comment_gateway = comment_gateway
        self._comment_service = comment_service
        self._access_service = access_service
        self._id_provider = id_provider

    async def __call__(self, data: CommentId) -> None:
        comment = await self._comment_gateway.get_comment(data)
        if comment is None:
            raise NotFound(f"Комментарий не найден")

        try:
            self._access_service.ensure_can_delete_comment(
                is_auth=self._id_provider.is_auth(),
                user_id=self._id_provider.user_id(),
                user_state=self._id_provider.user_state(),
                comment_author_id=comment.author_id,
                permissions=self._id_provider.permissions(),
            )
        except domain_exceptions.AccessDenied as error:
            raise Forbidden(str(error))
        except domain_exceptions.AuthenticationError as error:
            raise Unauthorized(str(error))

        if comment.state == CommentState.DELETED:
            raise InvalidData(f"Комментарий уже удален")

        new_comment = self._comment_service.update_comment(
            comment=comment,
            content=comment.content,
            state=CommentState.DELETED,
        )
        await self._comment_gateway.save_comment(new_comment)
