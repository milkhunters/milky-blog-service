from typing import Protocol

from mbs.application.common.comment_gateway import CommentReader, CommentRater
from mbs.application.common.exceptions import NotFound, Unauthorized, Forbidden
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor
from mbs.domain.models import CommentId
from mbs.domain.services.access import AccessService
import mbs.domain.exceptions as domain_exceptions


class CommentGateway(CommentReader, CommentRater, Protocol):
    pass


class RateComment(Interactor[CommentId, None]):

    def __init__(
            self,
            comment_gateway: CommentGateway,
            access_service: AccessService,
            id_provider: IdProvider
    ):
        self._comment_gateway = comment_gateway
        self._access_service = access_service
        self._id_provider = id_provider

    async def __call__(self, data: CommentId) -> None:
        comment = await self._comment_gateway.get_comment(data)
        if not comment:
            raise NotFound("Комментарий не найден")

        try:
            self._access_service.ensure_can_rate_comment(
                is_auth=self._id_provider.is_auth(),
                permissions=self._id_provider.permissions(),
                user_state=self._id_provider.user_state(),
                comment_state=comment.state
            )
        except domain_exceptions.AccessDenied as error:
            raise Forbidden(str(error))
        except domain_exceptions.AuthenticationError as error:
            raise Unauthorized(str(error))

        await self._comment_gateway.rate_comment(data, self._id_provider.user_id())
