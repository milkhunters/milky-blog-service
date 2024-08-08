import uuid

from sqlalchemy import select, bindparam, text, UUID, Integer, delete, func
from sqlalchemy.orm import aliased

from mbs.adapters.database import models
from sqlalchemy.ext.asyncio import AsyncSession

from mbs.application.common.comment_gateway import CommentReader, CommentWriter, CommentRemover
from mbs.domain.models import CommentId, Comment, ArticleId, File


class CommentGateway(CommentReader, CommentWriter, CommentRemover):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_comment(self, comment_id: CommentId) -> Comment | None:

        # todo to gather
        comment = (await self._session.execute(select(models.Comment).where(id=comment_id))).scalars().first()
        branch = (await self._session.execute(select(models.CommentTree).where(
            ancestor_id=comment_id,
            descendant_id=comment_id
        ))).scalars().first()

        if comment:
            return Comment(
                id=comment.id,
                content=comment.content,
                author_id=comment.author_id,
                article_id=branch.article_id,
                parent_id=branch.nearest_ancestor_id,
                state=comment.state,
                created_at=comment.create_time,
                updated_at=comment.update_time
            )

    async def get_comment_with_files(self, comment_id: CommentId) -> tuple[Comment, list[File]] | None:
        files_subquery = (
            select(
                models.CommentFile.comment_id,
                func.array_agg(models.File.id).label("files")
            )
            .join(models.File, models.CommentFile.file_id == models.File.id)
            .group_by(models.CommentFile.comment_id)
            .subquery()
        )

        files_alias = aliased(files_subquery, name="files")

        # todo to gather
        comment, files = (await self._session.execute(
            select(
                models.Comment,
                files_alias.c.files
            )
            .where(id=comment_id)
            .outerjoin(files_alias, models.Comment.id == files_alias.c.comment_id)
        )).scalars().first()
        branch = (await self._session.execute(select(models.CommentTree).where(
            ancestor_id=comment_id,
            descendant_id=comment_id
        ))).scalars().first()

        if comment:
            return Comment(
                id=comment.id,
                content=comment.content,
                author_id=comment.author_id,
                article_id=branch.article_id,
                parent_id=branch.nearest_ancestor_id,
                state=comment.state,
                created_at=comment.create_time,
                updated_at=comment.update_time
            ), [
                File(
                    id=file.id,
                    filename=file.filename,
                    content_type=file.content_type,
                    is_uploaded=file.is_uploaded,
                    created_at=file.create_time,
                    updated_at=file.update_time
                ) for file in files
            ] if files else []

    async def get_comments_with_files(self, article_id: ArticleId) -> list[tuple[Comment, int, list[File]]]:
        files_subquery = (
            select(
                models.CommentFile.comment_id,
                func.array_agg(models.File.id).label("files")
            )
            .join(models.File, models.CommentFile.file_id == models.File.id)
            .group_by(models.CommentFile.comment_id)
            .subquery()
        )
        files_alias = aliased(files_subquery, name="files")

        query = (
            select(
                models.Comment,
                models.CommentTree.article_id,
                models.CommentTree.nearest_ancestor_id,
                models.CommentTree.level,
                files_alias.c.files
            )
            .join(models.CommentTree, models.Comment.id == models.CommentTree.descendant_id)
            .where(models.CommentTree.article_id == article_id)
            .where(models.CommentTree.ancestor_id == models.Comment.id)
            .outerjoin(files_alias, models.Comment.id == files_alias.c.comment_id)
            .order_by(models.Comment.id.asc())
        )
        result = (await self._session.execute(query)).fetchall()
        return [
            (
                Comment(
                    id=comment.id,
                    content=comment.content,
                    author_id=comment.author_id,
                    article_id=article_id,
                    parent_id=parent_id,
                    state=comment.state,
                    created_at=comment.create_time,
                    updated_at=comment.update_time
                ),
                level,
                [
                    File(
                        id=file.id,
                        filename=file.filename,
                        content_type=file.content_type,
                        is_uploaded=file.is_uploaded,
                        created_at=file.create_time,
                        updated_at=file.update_time
                    ) for file in files
                ] if files else []
            )
            for comment, article_id, parent_id, level, files in result
        ]

    async def save_comment(self, comment: Comment) -> None:
        async with self._session.begin() as transaction:
            model = (await self._session.execute(select(models.Comment).filter_by(id=comment.id))).scalars().first()

            if model:
                model.content = comment.content
                model.state = comment.state
                model.created_at = comment.created_at
                model.updated_at = comment.updated_at
            else:
                model = models.Comment(
                    id=comment.id,
                    content=comment.content,
                    author_id=comment.author_id,
                    state=comment.state,
                    created_at=comment.created_at,
                    updated_at=comment.updated_at,
                )
                transaction.session.add(model)

                parent_level = - 1
                if comment.parent_id:
                    branch = (await self._session.execute(select(models.CommentTree).where(
                        ancestor_id=comment.parent_id,
                        descendant_id=comment.parent_id
                    ))).scalars().first()
                    parent_level = branch.level

                sql_raw = text("""
                    INSERT INTO comment_tree (ancestor_id, descendant_id, nearest_ancestor_id, article_id, level)
                    SELECT ancestor_id, :new_comment_id, :parent_id, :article_id, :parent_level
                    FROM comment_tree
                    WHERE descendant_id = :parent_id
                    UNION ALL SELECT :new_comment_id, :new_comment_id, :parent_id, :article_id, :parent_level
                """)
                params = {
                    'new_comment_id': comment.id,
                    'parent_id': comment.parent_id,
                    'article_id': comment.article_id,
                    'parent_level': parent_level + 1,
                }
                sql_raw = sql_raw.bindparams(
                    bindparam('new_comment_id', type_=UUID),
                    bindparam('parent_id', type_=UUID),
                    bindparam('article_id', type_=UUID),
                    bindparam('parent_level', type_=Integer),
                ).columns()
                await transaction.session.execute(sql_raw, params)

            await transaction.commit()

    async def delete_article_comments(self, article_id: ArticleId) -> None:
        async with self._session.begin() as transaction:
            select_query = (
                select(models.CommentTree.descendant_id)
                .where(models.CommentTree.ancestor_id == models.CommentTree.descendant_id)
                .where(models.CommentTree.article_id == article_id)
            )

            delete_query = (
                delete(models.Comment)
                .where(models.Comment.id.in_(select_query))
            )

            delete_branch_query = (
                delete(models.CommentTree)
                .where(models.CommentTree.article_id == article_id)
            )

            await transaction.session.execute(delete_query)
            await transaction.session.execute(delete_branch_query)
            await transaction.commit()
