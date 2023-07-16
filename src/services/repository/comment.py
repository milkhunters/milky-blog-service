import uuid

from sqlalchemy import insert, select, bindparam, text, literal, union_all, UUID, Integer

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
        sql_raw = text("""
            INSERT INTO comment_tree (ancestor_id, descendant_id, nearest_ancestor_id, article_id, level)
            SELECT ancestor_id, :new_comment_id, :parent_id, :article_id, :parent_level
            FROM comment_tree
            WHERE descendant_id = :parent_id
            UNION ALL SELECT :new_comment_id, :new_comment_id, :parent_id, :article_id, :parent_level
        """)
        params = {
            'new_comment_id': new_comment_id,
            'parent_id': parent_id,
            'article_id': article_id,
            'parent_level': parent_level + 1,
        }
        sql_raw = sql_raw.bindparams(
            bindparam('new_comment_id', type_=UUID),
            bindparam('parent_id', type_=UUID),
            bindparam('article_id', type_=UUID),
            bindparam('parent_level', type_=Integer),
        ).columns()
        result = await self.session.execute(sql_raw, params)
        await self.session.commit()
        return result
