from typing import Protocol

from mbs.application.common.article_gateway import ArticleReader, ArticleRemover
from mbs.application.common.comment_gateway import CommentRemover
from mbs.application.common.exceptions import NotFound, Unauthorized, Forbidden
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor
from mbs.domain.models import ArticleId
from mbs.domain.services.access import AccessService
import mbs.domain.exceptions as domain_exceptions


class ArticleGateway(ArticleReader, ArticleRemover, Protocol):
    pass


class DeleteArticle(Interactor[ArticleId, None]):

    def __init__(
            self,
            article_gateway: ArticleGateway,
            comment_remover: CommentRemover,
            access_service: AccessService,
            id_provider: IdProvider,
    ):
        self._article_gateway = article_gateway
        self._comment_remover = comment_remover
        self._access_service = access_service
        self._id_provider = id_provider

    async def __call__(self, data: ArticleId) -> None:

        article = await self._article_gateway.get_article(data)
        if not article:
            raise NotFound("Публикация не найдена")

        try:
            self._access_service.ensure_can_delete_article(
                is_auth=self._id_provider.is_auth(),
                user_id=self._id_provider.user_id(),
                article_author_id=article.author_id,
                permissions=self._id_provider.permissions(),
                user_state=self._id_provider.user_state(),
            )
        except domain_exceptions.AuthenticationError as error:
            raise Unauthorized(str(error))
        except domain_exceptions.AccessDenied as error:
            raise Forbidden(str(error))

        await self._article_gateway.remove_article(data)
        await self._comment_remover.delete_article_comments(data)
