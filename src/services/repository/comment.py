import uuid

from src.models import tables
from src.services.repository.base import BaseRepository


class CommentRepo(BaseRepository[tables.Comment]):
    table = tables.Comment

    async def delete_comments(self, comment_ids: list[int]) -> None:
        await self.session.execute(
            self.table.delete().where(self.table.id.in_(comment_ids))
        )


class CommentTreeRepo(BaseRepository[tables.CommentTree]):
    table = tables.CommentTree

    async def create_branch(
            self,
            parent_id: uuid.UUID,
            new_comment_id: uuid.UUID,
            article_id: uuid.UUID,
            parent_level: int
    ):
        sql_raw = """
            INSERT INTO comment_tree (ancestor_id, descendant_id, nearest_ancestor_id, article_id, level)
             SELECT ancestor_id, $1::int, $2::int, $3::int, $4::int
                FROM comment_tree
              WHERE descendant_id = $2::int
            UNION ALL SELECT $1::int, $1::int, $2::int, $3::int, $4::int
            """
        return await self.session.execute(
            sql_raw, (new_comment_id, parent_id, article_id, parent_level + 1)
        )  # TODO: параметры: словарь аля ':var' => var=some
