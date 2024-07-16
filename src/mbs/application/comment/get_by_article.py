from datetime import datetime
from typing import Protocol

from pydantic import BaseModel

import mbs.domain.exceptions as domain_exceptions
from mbs.application.common.article_gateway import ArticleReader
from mbs.application.common.comment_gateway import CommentReader, CommentRater
from mbs.application.common.exceptions import NotFound, Forbidden
from mbs.application.common.id_provider import IdProvider
from mbs.application.common.interactor import Interactor
from mbs.domain.models import CommentState, CommentId, UserId, ArticleId
from mbs.domain.services.access import AccessService


class CommentNode(BaseModel):
    id: CommentId
    content: str
    author_id: UserId
    parent_id: CommentId | None
    state: CommentState
    is_rated: bool
    answers: list['CommentNode']
    level: int

    created_at: datetime
    updated_at: datetime | None


class CommentGateway(CommentReader, CommentRater, Protocol):
    pass


class GetArticleComments(Interactor[ArticleId, list[CommentNode]]):

    def __init__(
            self,
            article_reader: ArticleReader,
            comment_gateway: CommentGateway,
            access_service: AccessService,
            id_provider: IdProvider,
    ):
        self._article_reader = article_reader
        self._comment_gateway = comment_gateway
        self._access_service = access_service
        self._id_provider = id_provider

    async def __call__(self, data: ArticleId) -> list[CommentNode]:
        article = await self._article_reader.get_article(data)
        if article is None:
            raise NotFound("Публикация не найдена")

        try:
            self._access_service.ensure_can_get_published_comment(
                permissions=self._id_provider.permissions()
            )
        except domain_exceptions.AccessDenied as error:
            raise Forbidden(str(error))

        can_look_deleted = True
        try:
            self._access_service.ensure_can_get_comment(
                is_auth=self._id_provider.is_auth(),
                user_state=self._id_provider.user_state(),
                permissions=self._id_provider.permissions(),
            )
        except domain_exceptions.DomainError:
            can_look_deleted = False

        raw_comments = await self._comment_gateway.get_comments(data)

        rated_states = await self._comment_gateway.is_comments_rated(
            comment_ids=[comment.id for comment, _ in raw_comments],
            user_id=self._id_provider.user_id()
        )

        comment_list = []
        for (comment, level), is_rated in zip(raw_comments, rated_states):
            if comment.state == CommentState.DELETED and not can_look_deleted:
                comment.content = "Комментарий удален"

            comment_list.append(CommentNode(
                **comment.model_dump(),
                is_rated=is_rated,
                answers=[],
                parent_id=comment.parent_id,
                level=level
            ))

        comment_tree = []
        for comment in comment_list:
            if comment.level == 0:
                comment_tree.append(comment)
            for descendant in comment_list:
                if descendant.parent_id == comment.id:
                    comment.answers.append(descendant)
        return comment_tree
