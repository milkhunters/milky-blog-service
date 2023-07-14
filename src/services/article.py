import uuid
from typing import Literal

from src import exceptions
from src.models import schemas
from src.models.auth import BaseUser
from src.models.role import Role, MainRole as M, AdditionalRole as A
from src.models.state import ArticleState
from src.services.auth import role_filter
from src.services.repository import CommentTreeRepo, CommentRepo
from src.services.repository.article import ArticleRepo
from src.services.repository.tag import TagRepo


class ArticleApplicationService:

    def __init__(
            self,
            current_user: BaseUser,
            article_repo: ArticleRepo,
            tag_repo: TagRepo,
            comment_tree_repo: CommentTreeRepo,
            comment_repo: CommentRepo

    ):
        self._current_user = current_user
        self._repo = article_repo
        self._tag_repo = tag_repo
        self._tree_repo = comment_tree_repo
        self._comment_repo = comment_repo

    @role_filter(min_role=Role(M.GUEST, A.ONE))
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
        :param per_page: количество статей на странице (всегда >= 1 но <= per_page_limit)
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
                        self._current_user.role < Role(M.ADMIN, A.ONE)
                )
        ):
            raise exceptions.AccessDenied("Нет доступа")

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

    @role_filter(min_role=Role(M.GUEST, A.ONE))
    async def get_article(self, article_id: uuid.UUID) -> schemas.Article:
        article = await self._repo.get(id=article_id)
        if not article:
            raise exceptions.NotFound("Статья не найдена")

        if all(
                (
                        article.state != ArticleState.PUBLISHED,
                        article.owner_id != self._current_user.id,
                        self._current_user.role < Role(M.ADMIN, A.ONE)
                )
        ):
            raise exceptions.AccessDenied("Статья не опубликована")

        return schemas.Article.model_validate(article)

    @role_filter(min_role=Role(M.MODER, A.ONE))
    async def create_article(self, data: schemas.ArticleCreate) -> schemas.Article:
        _ = await self._repo.create(
            **data.model_dump(exclude_unset=True, exclude={"tags"}),
            owner_id=self._current_user.id
        )
        article = await self._repo.get(id=_.id)
        # Добавление тегов
        for tag_title in data.tags:
            tag = await self._tag_repo.get(title=tag_title)
            if not tag:
                tag = await self._tag_repo.create(title=tag_title)
            article.tags.append(tag)
        await self._repo.session.commit()
        return schemas.Article.model_validate(article)

    @role_filter(min_role=Role(M.MODER, A.ONE))
    async def update_article(self, article_id: uuid.UUID, data: schemas.ArticleUpdate) -> None:
        article = await self._repo.get(id=article_id)
        if not article:
            raise exceptions.NotFound("Статья не найдена")

        if article.owner_id != self._current_user.id and self._current_user.role < Role(M.ADMIN, A.ONE):
            raise exceptions.AccessDenied("Вы не являетесь владельцем статьи")

        await self._repo.update(article_id, **data.model_dump(exclude_unset=True))

    @role_filter(min_role=Role(M.MODER, A.ONE))
    async def delete_article(self, article_id: uuid.UUID) -> None:
        # todo
        article = await self._repo.get(id=article_id)
        if not article:
            raise exceptions.NotFound("Статья не найдена")

        if article.owner_id != self._current_user.id and self._current_user.role < Role(M.ADMIN, A.ONE):
            raise exceptions.AccessDenied("Вы не являетесь владельцем статьи")

        await self._repo.delete(id=article_id)

        comment_ids = await self._comment_repo.get_id_comments_in_article(article_id)
        if comment_ids:
            await self._comment_repo.delete_comments(comment_ids)

        await self._tree_repo.delete_all_branches(article_id)
