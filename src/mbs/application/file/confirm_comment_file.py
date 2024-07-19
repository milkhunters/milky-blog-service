import logging
from typing import Protocol

from pydantic import BaseModel

from mbs.application.common.article_gateway import ArticleReader
from mbs.application.common.comment_gateway import CommentReader, CommentFile
from mbs.application.common.exceptions import NotFound, Unauthorized, Forbidden, InvalidData
from mbs.application.common.file_gateway import FileReader, FileWriter
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor
from mbs.application.common.storage_gateway import StorageReader
from mbs.domain.models import CommentId, FileId
from mbs.domain.services.access import AccessService
from mbs.domain.services.file import FileService
import mbs.domain.exceptions as domain_exceptions


class ConfirmCommentFileDTO(BaseModel):
    comment_id: CommentId
    file_id: FileId


class FileGateway(FileReader, FileWriter, Protocol):
    pass


class CommentGateway(CommentReader, CommentFile, Protocol):
    pass


class ConfirmCommentFile(Interactor[ConfirmCommentFileDTO, None]):

    def __init__(
            self,
            article_reader: ArticleReader,
            comment_gateway: CommentGateway,
            storage_reader: StorageReader,
            file_gateway: FileGateway,
            file_service: FileService,
            access_service: AccessService,
            id_provider: IdProvider
    ):
        self._article_reader = article_reader
        self._comment_gateway = comment_gateway
        self._storage_reader = storage_reader
        self._file_gateway = file_gateway
        self._file_service = file_service
        self._access_service = access_service
        self._id_provider = id_provider

    async def __call__(self, data: ConfirmCommentFileDTO) -> None:
        validator_err_map: dict[str, str] = dict()
        if not await self._comment_gateway.is_file_linked_to_comment(
                comment_id=data.article_id,
                file_id=data.file_id
        ):
            validator_err_map["file_id"] = "Файл не привязан к комментарию"

        comment = await self._comment_gateway.get_comment(data.comment_id)
        if not comment:
            validator_err_map["comment_id"] = "Комментарий не найден"

        if validator_err_map:
            raise InvalidData(validator_err_map)

        article = await self._article_reader.get_article(comment.article_id)

        try:
            self._access_service.ensure_can_upload_comment_file(
                is_auth=self._id_provider.is_auth(),
                user_id=self._id_provider.user_id(),
                permissions=article.permissions,
                user_state=article.user_state,
                comment_state=comment.state,
                comment_author_id=comment.author_id,
                article_state=article.state
            )
        except domain_exceptions.AuthenticationError as error:
            raise Unauthorized(str(error))
        except domain_exceptions.AccessDenied as error:
            raise Forbidden(str(error))

        file = await self._file_gateway.get_file(data.file_id)
        if not file:
            validator_err_map["file_id"] = "Файл не найден"
            logging.warning(f"File exists in Comment<->File but not found in File: {data.file_id}")
            raise InvalidData(validator_err_map)

        if file.is_uploaded:
            validator_err_map["file_id"] = "Файл уже подтвержден"
            raise InvalidData(validator_err_map)

        if not await self._storage_reader.is_exist_comment_object(
            comment_id=data.comment_id,
            file_id=data.file_id
        ):
            validator_err_map["file_id"] = "Файл не загружен"
            raise InvalidData(validator_err_map)

        new_file = self._file_service.make_uploaded(file)

        await self._file_gateway.save_file(new_file)
