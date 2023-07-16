"""
    Сервис для работы с комментариями

    Используется подход ...


"""
import uuid

from src.models import schemas
from src.models.auth import BaseUser
from src.models.role import Role, MainRole as M, AdditionalRole as A
from src.models.state import CommentState, ArticleState
from src.models.state import NotificationType

from src import exceptions
from src.services.auth import role_filter
from src.services.repository import CommentRepo, ArticleRepo
from src.services.repository import CommentTreeRepo
from src.services.repository import NotificationRepo


class CommentApplicationService:
    def __init__(
            self,
            current_user: BaseUser,
            comment_repo: CommentRepo,
            comment_tree_repo: CommentTreeRepo,
            notify_repo: NotificationRepo,
            article_repo: ArticleRepo
    ):
        self._current_user = current_user
        self._repo = comment_repo
        self._tree_repo = comment_tree_repo
        self._notification_repo = notify_repo
        self._article_repo = article_repo

    @role_filter(min_role=Role(M.USER, A.ONE))
    async def add_comment(
            self,
            article_id: uuid.UUID,
            data: schemas.CommentCreate,
            parent_id: uuid.UUID = None
    ) -> schemas.Comment:
        """
        Добавить комментарий к публикации

        :param article_id: идентификатор публикации
        :param data: данные комментария
        :param parent_id: идентификатор родительского комментария
        :return:

        """

        article = await self._article_repo.get(id=article_id)
        if article is None:
            raise exceptions.NotFound("Публикация не найдена")

        if article.state != ArticleState.PUBLISHED:
            raise exceptions.BadRequest("Нельзя добавить комментарий к неопубликованной публикации")

        parent = None
        parent_level = -1
        if parent_id is not None:
            parent = await self._repo.get(id=parent_id)
            if parent is None:
                raise exceptions.NotFound("Родительский комментарий не найден")

            parent_as_node = await self._tree_repo.get(ancestor_id=parent_id, descendant_id=parent_id)
            if parent_as_node is None:
                raise exceptions.NotFound("Родительский комментарий не связан с публикацией")

            if parent_as_node.article_id != article_id:
                raise exceptions.BadRequest(f"Комментарий не принадлежит публикации с id:{article_id}")

            parent_level = parent_as_node.level

        if parent and parent.state == CommentState.DELETED:
            raise exceptions.BadRequest("Родительский комментарий удален")

        new_comment = await self._repo.create(
            content=data.content,
            owner_id=self._current_user.id,
        )

        if parent and parent.owner_id != new_comment.owner_id:
            await self._notification_repo.create(
                owner_id=parent.owner_id,
                type_id=NotificationType.COMMENT_ANSWER,
                content_id=new_comment.id,
                content=f"{new_comment.owner.username} ответил на Ваш комментарий"
            )

        await self._tree_repo.create_branch(
            parent_id=parent_id,
            new_comment_id=new_comment.id,
            article_id=article_id,
            parent_level=parent_level
        )
        return schemas.Comment.model_validate(new_comment)

    @role_filter(min_role=Role(M.GUEST, A.ONE))
    async def get_comment(self, comment_id: uuid.UUID) -> schemas.Comment:
        comment = await self._repo.get(id=comment_id)
        if comment is None:
            raise exceptions.NotFound(f"Комментарий c id:{comment_id} не найден")

        if comment.state == CommentState.DELETED and self._current_user.role < Role(M.ADMIN, A.ONE):
            raise exceptions.NotFound(f"Комментарий c id:{comment_id} не найден")

        return schemas.Comment.model_validate(comment)

    @role_filter(min_role=Role(M.GUEST, A.ONE))
    async def get_comments(self, article_id: uuid.UUID) -> list[schemas.CommentNode]:
        """
        Получить все комментарии публикации

        """
        raw = await self._tree_repo.get_comments(article_id)

        # Подготовка
        comment_list = []
        for obj, nearest_ancestor_id, level in raw:
            comment = schemas.Comment.model_validate(obj)
            if comment.state == CommentState.DELETED:
                if self._current_user.role < Role(M.ADMIN, A.ONE):
                    comment.content = "Комментарий удален"
                else:
                    comment.content = f"(Комментарий удален): {comment.content}"

            comment_list.append(schemas.CommentNode(
                **comment.model_dump(),
                answers=[],
                parent_id=nearest_ancestor_id,
                level=level
            ))

        # Сортировка
        comment_tree = []
        for comment in comment_list:
            if comment.level == 0:
                comment_tree.append(comment)
            for descendant in comment_list:
                if descendant.parent_id == comment.id:
                    comment.answers.append(descendant)
        return comment_tree

    @role_filter(min_role=Role(M.USER, A.ONE))
    async def delete_comment(self, comment_id: uuid.UUID) -> None:
        """
        Удалить комментарий
        """
        comment = await self._repo.get(id=comment_id)
        if comment is None:
            raise exceptions.NotFound(f"Комментарий c id:{comment_id} не найден")

        if comment.state == CommentState.DELETED:
            raise exceptions.BadRequest(f"Комментарий c id:{comment_id} уже удален")

        if comment.owner_id != self._current_user.id and self._current_user.role < Role(M.ADMIN, A.ONE):
            raise exceptions.AccessDenied("Нельзя удалить чужой комментарий")

        await self._repo.update(id=comment_id, state=CommentState.DELETED)

    async def delete_all_comments(self, article_id: int) -> None:
        """
        Удалить все комментарии публикации
        (из бд)

        :param article_id:
        :return:
        """
        comment_ids = await self._repo.get_id_comments_in_article(article_id)
        await self._tree_repo.delete_all_branches(article_id)
        await self._repo.delete_comments(comment_ids)

    async def update_comment(self, comment_id: uuid.UUID, data: schemas.CommentUpdate) -> None:
        """
        Изменить комментарий

        :param comment_id:
        :param data:
        :return:
        """
        # comment = await cs.get_comment(id)
        # if not comment or (comment["state"] == CommentState.deleted):
        #     raise APIError(919)
        # if comment["owner_id"] != request.user.id:
        #     raise APIError(909)
        await self._repo.update(id=comment_id, content=data.content)

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
            if row["state"] == CommentState.DELETED:
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
