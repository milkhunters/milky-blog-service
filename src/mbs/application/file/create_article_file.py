from typing import Protocol

from pydantic import BaseModel

import mbs.domain.exceptions as domain_exceptions
from mbs.application.common.article_gateway import ArticleReader, ArticleFile
from mbs.application.common.exceptions import InvalidData, Unauthorized, Forbidden
from mbs.application.common.file_gateway import FileWriter
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor
from mbs.application.common.presigned_post_url import PreSignedPostUrl
from mbs.application.common.storage_gateway import StorageAccessLinkMaker
from mbs.domain.models import ArticleId, FileId
from mbs.domain.services.access import AccessService
from mbs.domain.services.file import FileService
from mbs.domain.services.validator import ValidatorService


class CreateArticleFileDTO(BaseModel):
    article_id: ArticleId
    filename: str
    content_type: str


class ArticleFileResult(BaseModel):
    file_id: FileId
    upload_url: PreSignedPostUrl


class ArticleGateway(ArticleReader, ArticleFile, Protocol):
    pass


class CreateArticleFile(Interactor[CreateArticleFileDTO, ArticleFileResult]):

    def __init__(
            self,
            article_gateway: ArticleGateway,
            file_writer: FileWriter,
            file_service: FileService,
            storage_access_link_maker: StorageAccessLinkMaker,
            access_service: AccessService,
            validator: ValidatorService,
            id_provider: IdProvider,
    ):
        self._article_gateway = article_gateway
        self._file_writer = file_writer
        self._file_service = file_service
        self._storage_access_link_maker = storage_access_link_maker
        self._access_service = access_service
        self._validator = validator
        self._id_provider = id_provider

    async def __call__(self, data: CreateArticleFileDTO) -> ArticleFileResult:
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

        article = await self._article_gateway.get_article(data.article_id)
        if not article:
            validator_err_map["article_id"] = "Публикация не найдена"

        if validator_err_map:
            raise InvalidData(validator_err_map)

        try:
            self._access_service.ensure_can_upload_article_file(
                is_auth=self._id_provider.is_auth(),
                user_id=self._id_provider.user_id(),
                permissions=article.permissions,
                user_state=article.user_state,
                article_author_id=article.author_id,
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
        await self._article_gateway.link_file_to_article(
            article_id=data.article_id,
            file_id=file.id
        )
        url = await self._storage_access_link_maker.make_article_upload_link(
            article_id=data.article_id,
            file_id=file.id,
            content_type=file.content_type,
            content_length=(1, 500 * 1024 * 1024),  # 500mb
            expires_in=30 * 60  # 30 min
        )

        return ArticleFileResult(
            file_id=file.id,
            upload_url=url
        )
