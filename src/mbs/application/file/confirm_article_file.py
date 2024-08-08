import logging
from typing import Protocol

from pydantic import BaseModel

from mbs.application.common.article_gateway import ArticleReader, ArticleFile
from mbs.application.common.exceptions import NotFound, Unauthorized, Forbidden, InvalidData
from mbs.application.common.file_gateway import FileReader, FileWriter
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor
from mbs.application.common.storage_gateway import StorageReader
from mbs.domain.models import ArticleId, FileId
from mbs.domain.services.access import AccessService
from mbs.domain.services.file import FileService
import mbs.domain.exceptions as domain_exceptions


class ConfirmArticleFileDTO(BaseModel):
    article_id: ArticleId
    file_id: FileId


class FileGateway(FileReader, FileWriter, Protocol):
    pass


class ArticleGateway(ArticleReader, ArticleFile, Protocol):
    pass


class ConfirmArticleFile(Interactor[ConfirmArticleFileDTO, None]):

    def __init__(
            self,
            article_gateway: ArticleGateway,
            storage_reader: StorageReader,
            file_gateway: FileGateway,
            file_service: FileService,
            access_service: AccessService,
            id_provider: IdProvider
    ):
        self._article_gateway = article_gateway
        self._storage_reader = storage_reader
        self._file_gateway = file_gateway
        self._file_service = file_service
        self._access_service = access_service
        self._id_provider = id_provider

    async def __call__(self, data: ConfirmArticleFileDTO) -> None:
        validator_err_map: dict[str, str] = dict()
        if not await self._article_gateway.is_file_linked_to_article(
            article_id=data.article_id,
            file_id=data.file_id
        ):
            validator_err_map["file_id"] = "Файл не привязан к публикации"

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

        file = await self._file_gateway.get_file(data.file_id)
        if not file:
            validator_err_map["file_id"] = "Файл не найден"
            logging.warning(f"File exists in Article<->File but not found in File: {data.file_id}")
            raise InvalidData(validator_err_map)

        if file.is_uploaded:
            validator_err_map["file_id"] = "Файл уже подтвержден"
            raise InvalidData(validator_err_map)

        if not await self._storage_reader.is_exist_article_object(
            article_id=data.article_id,
            file_id=data.file_id
        ):
            validator_err_map["file_id"] = "Файл не загружен"
            raise InvalidData(validator_err_map)

        new_file = self._file_service.make_uploaded(file)

        await self._file_gateway.save_file(new_file)
