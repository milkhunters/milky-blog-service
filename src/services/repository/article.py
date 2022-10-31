from typing import List, Optional, Union
from tortoise.expressions import Q

from models import schemas
from models import tables
from .base import BaseRepo


class ArticleRepo(BaseRepo[tables.Article, schemas.Article]):
    pass


class CommentRepo(BaseRepo[tables.Comment, schemas.Comment]):
    # todo: проверить работоспособность и использовать для других repo

    async def get(self, *args, **kwargs) -> Union[List[schemas.Comment], schemas.Comment, None]:
        # TODO: переписать
        return await self.table.filter(*args, **kwargs).prefetch_related("user").all()

    async def delete_comments(self, comment_ids: list[int]) -> None:
        """
        Удалить комментарии
        (полное удаление из бд)

        :param comment_ids: список id комментариев
        :return:
        """
        if not comment_ids:
            return None
        await self.table.filter(
            Q(*(Q(id=comment_id) for comment_id in comment_ids), join_type="OR")
        ).delete()


class CommentTreeRepo(BaseRepo[tables.CommentTree, schemas.CommentBranch]):

    async def create_branch(self, parent_id: int, new_comment_id: int, article_id: int, parent_level: int):
        sql_raw = """
            INSERT INTO comment_tree (ancestor_id, descendant_id, nearest_ancestor_id, article_id, level)
             SELECT ancestor_id, $1::int, $2::int, $3::int, $4::int
                FROM comment_tree
              WHERE descendant_id = $2::int
            UNION ALL SELECT $1::int, $1::int, $2::int, $3::int, $4::int
            """
        return await self.table.connection.execute_query_dict(
            sql_raw, [new_comment_id, parent_id, article_id, parent_level + 1]
        )  # TODO: привести в ORM вид

    async def delete_all_branches(self, article_id: int) -> None:
        """
        Удалить все ветки комментариев публикации

        :param article_id: ид публикации
        :return:
        """
        await self.table.filter(article_id=article_id).delete()
