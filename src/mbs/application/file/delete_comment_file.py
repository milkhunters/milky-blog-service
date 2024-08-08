from typing import Protocol

from pydantic import BaseModel

from mbs.application.common.article_gateway import ArticleReader
from mbs.application.common.comment_gateway import CommentReader, CommentFile
from mbs.application.common.exceptions import InvalidData, Forbidden, Unauthorized
from mbs.application.common.file_gateway import FileRemover
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor
from mbs.application.common.storage_gateway import StorageRemover
from mbs.domain.models import CommentId, FileId
from mbs.domain.services.access import AccessService
import mbs.domain.exceptions as domain_exceptions


class DeleteCommentFileDTO(BaseModel):
    comment_id: CommentId
    file_id: FileId


class CommentGateway(CommentReader, CommentFile, Protocol):
    pass


class DeleteCommentFile(Interactor[DeleteCommentFileDTO, None]):

    def __init__(
            self,
            article_reader: ArticleReader,
            comment_gateway: CommentGateway,
            file_remover: FileRemover,
            storage_remover: StorageRemover,
            access_service: AccessService,
            id_provider: IdProvider,
    ):
        self._article_reader = article_reader
        self._comment_gateway = comment_gateway
        self._file_remover = file_remover
        self._storage_remover = storage_remover
        self._access_service = access_service
        self._id_provider = id_provider

    async def __call__(self, data: DeleteCommentFileDTO) -> None:
        validator_err_map: dict[str, str] = dict()

        comment = await self._comment_gateway.get_comment(data.comment_id)
        if not comment:
            validator_err_map["comment_id"] = "Комментарий не найден"
            raise InvalidData(validator_err_map)

        if not await self._comment_gateway.is_file_linked_to_comment(data.comment_id, data.file_id):
            validator_err_map["file_id"] = "Файл не привязан к комментарию"
            raise InvalidData(validator_err_map)

        article = await self._article_reader.get_article(comment.article_id)

        try:
            self._access_service.ensure_can_delete_comment_file(
                is_auth=self._id_provider.is_auth(),
                user_state=self._id_provider.user_state(),
                permissions=self._id_provider.permissions(),
                user_id=self._id_provider.user_id(),
                comment_author_id=comment.author_id,
                comment_state=comment.state,
                article_state=article.state,
            )
        except domain_exceptions.AuthenticationError as error:
            raise Unauthorized(str(error))
        except domain_exceptions.AccessDenied as error:
            raise Forbidden(str(error))

        await self._comment_gateway.unlink_file_from_comment(data.article_id, data.file_id)

        # todo to gather
        await self._file_remover.remove_file(data.file_id)
        await self._storage_remover.remove_article_object(data.article_id, data.file_id)
