import uuid
import datetime

from mbs.domain.models import Comment, CommentState, UserId, ArticleId, CommentId


class CommentService:

    def create_comment(self, content: str, author_id: UserId, article_id: ArticleId, parent_id: CommentId | None):
        return Comment(
            id=uuid.uuid4(),
            content=content,
            author_id=author_id,
            article_id=article_id,
            parent_id=parent_id,
            state=CommentState.PUBLISHED,
            created_at=datetime.datetime.now(datetime.UTC),
            updated_at=None
        )

    def update_comment(
            self,
            comment: Comment,
            content: str,
            state: CommentState,
    ):
        return Comment(
            id=comment.id,
            content=content,
            author_id=comment.author_id,
            state=state,
            created_at=comment.created_at,
            updated_at=datetime.datetime.now(datetime.UTC)
        )