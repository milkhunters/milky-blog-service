from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from mbs.domain.models import UserId, ArticleId
from mbs.domain.models.comment_state import CommentState

type CommentId = UUID


class Comment(BaseModel):
    id: CommentId
    content: str
    author_id: UserId
    article_id: ArticleId
    parent_id: CommentId | None
    state: CommentState

    created_at: datetime
    updated_at: datetime | None
