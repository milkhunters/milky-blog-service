from typing import Protocol

from pydantic import BaseModel

import mbs.domain.exceptions as domain_exceptions
from mbs.application.common.article_gateway import ArticleReader
from mbs.application.common.comment_gateway import CommentReader, CommentFile
from mbs.application.common.exceptions import InvalidData, Unauthorized, Forbidden
from mbs.application.common.file_gateway import FileWriter
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor
from mbs.application.common.presigned_post_url import PreSignedPostUrl
from mbs.application.common.storage_gateway import StorageAccessLinkMaker
from mbs.domain.models import CommentId, FileId
from mbs.domain.services.access import AccessService
from mbs.domain.services.file import FileService
from mbs.domain.services.validator import ValidatorService


class CreateCommentFileDTO(BaseModel):
    comment_id: CommentId
    filename: str
    content_type: str


class CommentFileResult(BaseModel):
    file_id: FileId
    upload_url: PreSignedPostUrl


class CommentGateway(CommentReader, CommentFile, Protocol):
    pass


class CreateCommentFile(Interactor[CreateCommentFileDTO, CommentFileResult]):

    def __init__(
            self,
            comment_gateway: CommentGateway,
            article_reader: ArticleReader,
            file_writer: FileWriter,
            file_service: FileService,
            storage_access_link_maker: StorageAccessLinkMaker,
            access_service: AccessService,
            validator: ValidatorService,
            id_provider: IdProvider,
    ):
        self._comment_gateway = comment_gateway
        self._article_reader = article_reader
        self._file_writer = file_writer
        self._file_service = file_service
        self._storage_access_link_maker = storage_access_link_maker
        self._access_service = access_service
        self._validator = validator
        self._id_provider = id_provider

    async def __call__(self, data: CreateCommentFileDTO) -> CommentFileResult:
        validator_err_map: dict[str, str] = dict()

        try:
            self._validator.validate_filename(data.filename)
        except domain_exceptions.ValidationError as error:
            validator_err_map["filename"] = str(error)

        try:
            self._validator.validate_mime_content_type(data.content_type)
        except domain_exceptions.ValidationError as error:
            validator_err_map["content_type"] = str(error)

        if validator_err_map:
            raise InvalidData(validator_err_map)

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
                permissions=self._id_provider.permissions(),
                user_state=self._id_provider.user_state(),
                comment_state=comment.state,
                comment_author_id=comment.author_id,
                article_state=article.state
            )
        except domain_exceptions.AuthenticationError as error:
            raise Unauthorized(str(error))
        except domain_exceptions.AccessDenied as error:
            raise Forbidden(str(error))

        file = self._file_service.create_file(
            filename=data.filename,
            content_type=data.content_type
        )

        # todo to gather
        await self._file_writer.save_file(file)
        await self._comment_gateway.link_file_to_comment(
            comment_id=data.comment_id,
            file_id=file.id
        )
        url = await self._storage_access_link_maker.make_comment_upload_link(
            comment_id=data.comment_id,
            file_id=file.id,
            content_type=file.content_type,
            content_length=(1, 100 * 1024 * 1024),  # 100mb
            expires_in=30 * 60  # 30 min
        )

        return CommentFileResult(
            file_id=file.id,
            upload_url=url
        )
