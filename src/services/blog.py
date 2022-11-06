import math
from typing import Optional

import views
from exceptions import APIError
from models import schemas
from models.state import ArticleState, NotificationTypes, CommentState
from services.notification import NotificationService
from services.repository import ArticleRepo, CommentRepo
from services.repository.article import TagRepo, CommentTreeRepo


class BlogService:

    def __init__(
            self,
            article_repo: ArticleRepo = ArticleRepo(),
            comment_repo: CommentRepo = CommentRepo(),
            comment_tree_repo: CommentTreeRepo = CommentTreeRepo(),
            tag_repo: TagRepo = TagRepo()

    ):
        self._article_repo = article_repo
        self._comment_repo = comment_repo
        self._comment_tree_repo = comment_tree_repo
        self._tag_repo = tag_repo

    # ------------------ Статьи ------------------
    async def get_articles(
            self,
            page_num: int = 1,
            per_page: int = 10,
            order_by: str = "id",
            query: str = None,
            state: ArticleState = ArticleState.PUBLISHED,
            owner_id: int = None
    ) -> views.ArticlesResponse:
        """
        Получить список статей

        :param page_num: номер страницы (всегда >= 1)
        :param per_page: количество статей на странице (всегда >= 1 но <= per_page_limit)
        :param order_by: поле сортировки
        :param query: поисковый запрос (если необходим)
        :param state: статус статьи (по умолчанию только опубликованные), если None - то все статьи
        :param owner_id: id владельца статьи (если необходимо получить статьи только одного пользователя)
        :return:

        """

        if page_num < 1:
            raise APIError(919, "Номер страницы не может быть меньше 1")

        per_page_limit = 40

        # Подготовка входных данных
        order_by = order_by if order_by in ["id", "title", "create_time"] else "id"
        per_page = max(min(per_page, per_page_limit, 2147483646), 1)
        limit = min(page_num * per_page, 2147483646)
        skip = min((page_num - 1) * per_page, 2147483646)

        # поиск
        articles = await self._article_repo.search(
            query=query,
            fields=["title", "description", "content"],
            limit=limit + 1,
            skip=skip,
            order_by=order_by,
            **{"state": state} if state else {},
            **{"owner_id": owner_id} if owner_id else {}
        )

        return views.ArticlesResponse(
            items=[views.ArticleResponse.from_orm(article) for article in articles[:per_page]],
            current=page_num,
            next=(page_num + 1) if len(articles) > per_page else page_num,
            previous=(page_num - 1) if page_num > 1 else page_num
        )

    async def get_article(self, article_id: int) -> views.ArticleResponse:
        """
        Получить статью по id
        """
        article = await self._article_repo.get(id=article_id, fetch_related_fields=["owner"])
        if not article:
            raise APIError(919)
        return views.ArticleResponse.from_orm(article)

    async def create_article(self, article: schemas.ArticleCreate, owner_id: int) -> None:
        article = await self._article_repo.insert(
            title=article.title,
            owner_id=owner_id,
            content=article.content,
            state=article.state,
        )
        # добавление тегов
        for article_tag in article.tags:
            tag = await self._tag_repo.get(name=article_tag)
            if not tag:
                tag = await self._tag_repo.insert(name=article_tag)
            await self._article_repo.add_tag(article.id, tag.id)

    async def update_article(self, article_id: int, data: schemas.ArticleUpdate) -> None:
        article = await self._article_repo.get(id=article_id)
        if not article:
            raise APIError(919)
        await self._article_repo.update(article_id, **data.dict(exclude_unset=True))

    async def delete_article(self, article_id: int) -> None:
        article = await self._article_repo.get(id=article_id)
        if not article:
            raise APIError(919)
        await self._article_repo.delete(article_id)
        await self.delete_all_comments(article_id)

    # ------------------ Комментарии ------------------
    async def add_comment(self, article_id: int, content: str, owner_id: int, parent_id: int = 0):
        """
        Добавить комментарий к публикации

        :param article_id: ид публикации
        :param content: текст комментария
        :param owner_id: автор комментария
        :param parent_id: родитель, если это ответ (ид комментария)
        :return:

        # TODO: переписать

        """
        new_comment = await self._comment_repo.insert(
            content=content,
            owner_id=owner_id,  # TODO: изменено
        )

        parent_level = -1
        if parent_id != 0:
            parent = await self._comment_repo.get(id=parent_id) # Допустить вложенность в дерево комментариев, чтобы получить уровень вложенности
            parent_level = parent.level
            parent_owner_id = (await self.get_comment(parent_id)).owner.id
            if parent_owner_id != new_comment.owner_id:
                await NotificationService().create(
                    user_id=parent_owner_id,
                    notification_type=NotificationTypes.comment_answer,
                    data=new_comment.id
                )

        await self._comment_tree_repo.create_branch(
            parent_id=parent_id,
            new_comment_id=new_comment.id,
            article_id=article_id,
            parent_level=parent_level
        )
        return new_comment

    async def get_comment(self, comment_id: int) -> Optional[views.CommentResponse]:
        """
        Получить комментарий и его ветку (ответы)

        :param comment_id:
        :return:
        """
        raw_data = await self._db.get_raw_comment(comment_id)
        self._normalize(raw_data)
        if raw_data:
            return raw_data[0]
        return None

    async def get_comments(self, article_id: int) -> list[views.CommentResponse]:
        """
        Получить все комментарии публикации

        :param article_id:
        :return:
        """
        raw_data = await self._db.get_raw_comments(article_id)
        self._normalize(raw_data)
        return raw_data

    async def delete(self, comment_id) -> None:
        """
        Удалить комментарий
        (Изменить состояние - deleted)

        :param comment_id:
        :return:
        """
        await self._comment_repo.update(id=comment_id, state=CommentState.deleted)

    async def delete_all_comments(self, article_id: int) -> None:
        """
        Удалить все комментарии публикации
        (из бд)

        :param article_id:
        :return:
        """
        comment_ids = await self._comment_repo.get_id_comments_in_article(article_id)
        await self._comment_tree_repo.delete_all_branches(article_id)
        await self._comment_repo.delete_comments(comment_ids)

    @staticmethod
    def _normalize(raw_data: list[dict]) -> None:
        """
        Сортировка комментариев

        При этом:
            - добавляется поле <<answers>>
            - не включаются удаленные комментарии
            - удаляется поле <<state>>

        :param raw_data: список <<голых>> комментариев из бд
        :return:
        """
        assert type(raw_data) is list, TypeError("raw_data должно быть list, а не " + str(type(raw_data)))
        for i in reversed(range(len(raw_data))):
            # Берем последний эл-т
            row = raw_data[i]
            # Если комментарий удален
            if row["state"] == CommentState.deleted:
                row["content"] = "Комментарий удален"
                row["owner_id"] = 0
                row["first_name"] = ""
                row["last_name"] = ""
                row["username"] = ""

            # Есть ли поле "answers" в словаре raw
            if not ("answers" in row.keys()):
                # Добавляем недостающие поля
                row["answers"] = []

            # Есть ли у комментария родитель (ответ на коммент)
            if row["nearest_ancestor_id"] != 0:
                # Поиск индекса родителя
                parent_index = next((i for i, x in enumerate(raw_data) if x["id"] == row["nearest_ancestor_id"]), None)
                if parent_index is None:
                    # Ситуация, когда нет доступа к родителю:
                    # достается инфо только об одном комментарии
                    continue

                parent = raw_data[parent_index]
                # Есть ли поле "answers" в словаре родителя
                if not ("answers" in parent.keys()):
                    parent["answers"] = []

                # Перемещение коммента в первую ячейку списка ответивших
                parent["answers"].insert(0, row)
                raw_data.pop(i)
