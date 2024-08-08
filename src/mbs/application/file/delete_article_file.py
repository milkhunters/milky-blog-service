from typing import Protocol

from pydantic import BaseModel

from mbs.application.common.article_gateway import ArticleReader, ArticleFile
from mbs.application.common.exceptions import InvalidData, Forbidden, Unauthorized
from mbs.application.common.file_gateway import FileRemover
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor
from mbs.application.common.storage_gateway import StorageRemover
from mbs.domain.models import ArticleId, FileId
from mbs.domain.services.access import AccessService
import mbs.domain.exceptions as domain_exceptions


class DeleteArticleFileDTO(BaseModel):
    article_id: ArticleId
    file_id: FileId


class ArticleGateway(ArticleReader, ArticleFile, Protocol):
    pass


class DeleteArticleFile(Interactor[DeleteArticleFileDTO, None]):

    def __init__(
            self,
            article_gateway: ArticleGateway,
            file_remover: FileRemover,
            storage_remover: StorageRemover,
            access_service: AccessService,
            id_provider: IdProvider,
    ):
        self._article_gateway = article_gateway
        self._file_remover = file_remover
        self._storage_remover = storage_remover
        self._access_service = access_service
        self._id_provider = id_provider

    async def __call__(self, data: DeleteArticleFileDTO) -> None:
        validator_err_map: dict[str, str] = dict()

        article = await self._article_gateway.get_article(data.article_id)
        if not article:
            validator_err_map["article_id"] = "Публикация не найдена"
            raise InvalidData(validator_err_map)

        if not await self._article_gateway.is_file_linked_to_article(data.article_id, data.file_id):
            validator_err_map["file_id"] = "Файл не привязан к публикации"
            raise InvalidData(validator_err_map)

        try:
            self._access_service.ensure_can_delete_article_file(
                is_auth=self._id_provider.is_auth(),
                user_state=self._id_provider.user_state(),
                permissions=self._id_provider.permissions(),
                user_id=self._id_provider.user_id(),
                article_author_id=article.author_id,
                article_state=article.state,
            )
        except domain_exceptions.AuthenticationError as error:
            raise Unauthorized(str(error))
        except domain_exceptions.AccessDenied as error:
            raise Forbidden(str(error))

        await self._article_gateway.unlink_file_from_article(data.article_id, data.file_id)

        # todo to gather
        await self._file_remover.remove_file(data.file_id)
        await self._storage_remover.remove_article_object(data.article_id, data.file_id)
