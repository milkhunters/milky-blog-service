
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from mbs.domain.models.article_state import ArticleState
from mbs.domain.models.user_id import UserId
from mbs.domain.models.file import FileId

type ArticleId = UUID


class Article(BaseModel):
    id: ArticleId
    title: str
    poster: FileId | None
    content: str
    state: ArticleState
    views: int
    likes: int
    tags: list[str]
    author_id: UserId

    created_at: datetime
    updated_at: datetime | None
