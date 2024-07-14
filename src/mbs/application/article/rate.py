from typing import Protocol

from pydantic import BaseModel

from mbs.application.common.article_gateway import ArticleReader, ArticleRater
from mbs.application.common.exceptions import NotFound, Unauthorized, Forbidden
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor
from mbs.domain.models import ArticleId
from mbs.domain.services.access import AccessService
import mbs.domain.exceptions as domain_exceptions


class ArticleGateway(ArticleReader, ArticleRater, Protocol):
    pass


class RateArticle(Interactor[ArticleId, None]):

    def __init__(
            self,
            article_gateway: ArticleGateway,
            access_service: AccessService,
            id_provider: IdProvider
    ):
        self._article_gateway = article_gateway
        self._access_service = access_service
        self._id_provider = id_provider

    async def __call__(self, data: ArticleId) -> None:
        try:
            self._access_service.ensure_can_rate_article(
                is_auth=self._id_provider.is_auth(),
                permissions=self._id_provider.permissions(),
                user_state=self._id_provider.user_state(),
            )
        except domain_exceptions.AccessDenied as error:
            raise Forbidden(str(error))
        except domain_exceptions.AuthenticationError as error:
            raise Unauthorized(str(error))

        article = await self._article_gateway.get_article(data)
        if not article:
            raise NotFound("Статья не найдена")

        await self._article_gateway.rate_article(data, self._id_provider.user_id())
