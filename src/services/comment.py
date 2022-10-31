from typing import Optional

from models.state import CommentState
from models.state import NotificationTypes
from services.notification import NotificationService
from services.repository import CommentRepo
from services.repository import CommentTreeRepo


class CommentService:
    def __init__(
            self,
            comment_repo: CommentRepo = CommentRepo(),
            comment_tree_repo: CommentTreeRepo = CommentTreeRepo()
    ):
        self._repo = comment_repo
        self._tree_repo = comment_tree_repo

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
        new_comment = await self._repo.insert(
            content=content,
            owner_id=owner_id,  # TODO: изменено
        )

        parent_level = -1
        if parent_id != 0:
            parent = await self._repo.get(id=parent_id) # Допустить вложенность в дерево комментариев, чтобы получить уровень вложенности
            parent_level = parent.level
            parent_owner_id = (await self.get_comment(parent_id))["owner_id"]
            if parent_owner_id != new_comment.owner_id:
                await NotificationService().create_notification(
                    user_id=parent_owner_id,
                    notification_type=NotificationTypes.comment_answer,
                    data=new_comment.id
                )

        await self._db.create_branch(
            parent_id=parent_id,
            new_comment_id=new_comment.id,
            article_id=article_id,
            parent_level=parent_level
        )
        return new_comment

    async def get_comment(self, comment_id: int) -> Optional[dict]:
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

    async def get_comments(self, article_id: int) -> list[dict]:
        """
        Получить все комментарии публикации

        :param article_id:
        :return:
        """
        raw_data = await self._db.get_raw_comments(article_id)
        self._normalize(raw_data)
        return raw_data

    async def delete(self, comment_id):
        """
        Удалить комментарий
        (Изменить состояние - deleted)

        :param comment_id:
        :return:
        """
        await self._db.change_comment_state(comment_id, CommentState.deleted)

    async def delete_all_comments(self, article_id: int) -> None:
        """
        Удалить все комментарии публикации
        (из бд)

        :param article_id:
        :return:
        """
        comment_ids = await self._db.get_id_comments_in_article(article_id)
        await self._tree_repo.delete_all_branches(article_id)
        await self._repo.delete_comments(comment_ids)

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
