import uuid
from typing import Literal

from src import exceptions
from src.models import schemas
from src.models.access import AccessTags
from src.models.auth import BaseUser
from src.models.state import ArticleState, UserState, RateState
from src.services.auth.filters import state_filter
from src.services.auth.filters import access_filter
from src.services.repository import CommentTreeRepo, LikeRepo
from src.services.repository import CommentRepo
from src.services.repository import ArticleRepo
from src.services.repository import TagRepo


class ArticleApplicationService:

    def __init__(
            self,
            current_user: BaseUser,
            article_repo: ArticleRepo,
            tag_repo: TagRepo,
            comment_tree_repo: CommentTreeRepo,
            comment_repo: CommentRepo,
            like_repo: LikeRepo,

    ):
        self._current_user = current_user
        self._repo = article_repo
        self._tag_repo = tag_repo
        self._tree_repo = comment_tree_repo
        self._comment_repo = comment_repo
        self._like_repo = like_repo

    async def get_articles(
            self,
            page: int = 1,
            per_page: int = 10,
            order_by: Literal["title", "updated_at", "created_at"] = "created_at",
            query: str = None,
            state: ArticleState = ArticleState.PUBLISHED,
            owner_id: uuid.UUID = None
    ) -> list[schemas.ArticleSmall]:
        """
        Получить список статей

        :param page: номер страницы (всегда >= 1)
        :param per_page: количество статей на странице (всегда >= 1, но <= per_page_limit)
        :param order_by: поле сортировки
        :param query: поисковый запрос (если необходим)
        :param state: статус статьи (по умолчанию только опубликованные)
        :param owner_id: id владельца статьи (если необходимо получить статьи только одного пользователя)
        :return:

        """

        if page < 1:
            raise exceptions.NotFound("Страница не найдена")
        if per_page < 1:
            raise exceptions.BadRequest("Неверное количество элементов на странице")

        if all(
                (
                        state != ArticleState.PUBLISHED,
                        owner_id != self._current_user.id,
                        AccessTags.CAN_GET_PRIVATE_ARTICLES.value not in self._current_user.access
                )
        ):
            raise exceptions.AccessDenied("Вы не можете получить список приватных статей")

        if all(
                (
                        state != ArticleState.PUBLISHED,
                        owner_id == self._current_user.id,
                        AccessTags.CAN_GET_SELF_ARTICLES.value not in self._current_user.access
                )
        ):
            raise exceptions.AccessDenied("Вы не можете получить свой список приватных статей")

        if all(
                (
                        state == ArticleState.PUBLISHED,
                        AccessTags.CAN_GET_PUBLIC_ARTICLES.value not in self._current_user.access
                )
        ):
            raise exceptions.AccessDenied("Вы не можете получить список опубликованных статей")

        per_page_limit = 40

        # Подготовка входных данных
        per_page = min(per_page, per_page_limit, 2147483646)
        offset = min((page - 1) * per_page, 2147483646)

        # Выполнение запроса
        if query:
            articles = await self._repo.search(
                query=query,
                fields=["title", "content"],
                limit=per_page,
                offset=offset,
                order_by=order_by,
                **{"state": state} if state else {},
                **{"owner_id": owner_id} if owner_id else {}
            )
        else:
            articles = await self._repo.get_all(
                limit=per_page,
                offset=offset,
                order_by=order_by,
                **{"state": state} if state else {},
                **{"owner_id": owner_id} if owner_id else {}
            )
        return [schemas.ArticleSmall.model_validate(article) for article in articles]

    async def get_article(self, article_id: uuid.UUID) -> schemas.Article:
        article = await self._repo.get(id=article_id)
        if not article:
            raise exceptions.NotFound("Статья не найдена")

        if all(
                (
                        article.state != ArticleState.PUBLISHED,
                        article.owner_id != self._current_user.id,
                        AccessTags.CAN_GET_PRIVATE_ARTICLES.value not in self._current_user.access
                )
        ):
            raise exceptions.AccessDenied("Материал не опубликован")

        if all(
                (
                        article.state != ArticleState.PUBLISHED,
                        article.owner_id == self._current_user.id,
                        AccessTags.CAN_GET_SELF_ARTICLES.value not in self._current_user.access
                )
        ):
            raise exceptions.AccessDenied("Вы не можете просматривать свои приватные публикации")

        if all(
                (
                        article.state == ArticleState.PUBLISHED,
                        AccessTags.CAN_GET_PUBLIC_ARTICLES.value not in self._current_user.access
                )
        ):
            raise exceptions.AccessDenied("Вы не можете просматривать публичные публикации")

        # Views
        if article.state == ArticleState.PUBLISHED and article.owner_id != self._current_user.id:
            article.views += 1
            await self._repo.session.commit()
            await self._repo.session.refresh(article)

        # Likes
        article.likes_count = await self._like_repo.count(article_id=article_id)

        return schemas.Article.model_validate(article)

    @access_filter(AccessTags.CAN_CREATE_SELF_ARTICLES)
    @state_filter(UserState.ACTIVE)
    async def create_article(self, data: schemas.ArticleCreate) -> schemas.Article:
        _ = await self._repo.create(
            **data.model_dump(exclude_unset=True, exclude={"tags"}),
            owner_id=self._current_user.id
        )
        article = await self._repo.get(id=_.id)
        article.likes_count = 0
        # Добавление тегов
        for tag_title in data.tags:
            tag = await self._tag_repo.get(title=tag_title)
            if not tag:
                tag = await self._tag_repo.create(title=tag_title)
            article.tags.append(tag)
        await self._repo.session.commit()
        return schemas.Article.model_validate(article)

    @state_filter(UserState.ACTIVE)
    async def update_article(self, article_id: uuid.UUID, data: schemas.ArticleUpdate) -> None:
        article = await self._repo.get(id=article_id)
        if not article:
            raise exceptions.NotFound("Статья не найдена")

        if (
                article.owner_id != self._current_user.id and
                AccessTags.CAN_UPDATE_USER_ARTICLES.value not in self._current_user.access
        ):
            raise exceptions.AccessDenied("Вы не являетесь владельцем статьи")

        if (
                article.owner_id == self._current_user.id and
                AccessTags.CAN_UPDATE_SELF_ARTICLES.value not in self._current_user.access
        ):
            raise exceptions.AccessDenied("Вы не можете редактировать свои статьи")

        if data.tags:
            article.tags = []
            for tag_title in data.tags:
                tag = await self._tag_repo.get(title=tag_title)
                if not tag:
                    tag = await self._tag_repo.create(title=tag_title)
                article.tags.append(tag)
            await self._repo.session.commit()

        await self._repo.update(article_id, **data.model_dump(exclude_unset=True, exclude={"tags"}))

    @access_filter(AccessTags.CAN_RATE_ARTICLES)
    @state_filter(UserState.ACTIVE)
    async def rate_article(self, article_id: uuid.UUID, state: RateState) -> None:
        article = await self._repo.get(id=article_id)
        if not article:
            raise exceptions.NotFound("Статья не найдена")

        if article.owner_id == self._current_user.id:
            raise exceptions.BadRequest("Вы не можете оценивать свои статьи")

        like = await self._like_repo.get(article_id=article_id, owner_id=self._current_user.id)
        if state == RateState.LIKE:
            if like:
                raise exceptions.BadRequest("Вы уже поставили лайк")
            await self._like_repo.create(article_id=article_id, owner_id=self._current_user.id)
        elif state == RateState.NEUTRAL:
            if not like:
                raise exceptions.BadRequest("Вы еще не оценили статью")
            await self._like_repo.delete(like.id)

    @state_filter(UserState.ACTIVE)
    async def delete_article(self, article_id: uuid.UUID) -> None:
        article = await self._repo.get(id=article_id)
        if not article:
            raise exceptions.NotFound("Статья не найдена")

        if (
                article.owner_id != self._current_user.id and
                AccessTags.CAN_DELETE_USER_ARTICLES.value not in self._current_user.access
        ):
            raise exceptions.AccessDenied("Вы не являетесь владельцем статьи")

        if (
                article.owner_id == self._current_user.id and
                AccessTags.CAN_DELETE_SELF_ARTICLES.value not in self._current_user.access
        ):
            raise exceptions.AccessDenied("Вы не можете удалять свои статьи")

        await self._repo.delete(id=article_id)
        await self._comment_repo.delete_comments_by_article(article_id)
