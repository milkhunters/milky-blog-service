from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator

from mbs.domain.models.comment_state import CommentState
from mbs.domain.models.user_id import UserId

type CommentId = UUID


class Comment(BaseModel):
    id: CommentId
    content: str
    author_id: UserId
    state: CommentState

    created_at: datetime
    updated_at: datetime | None
