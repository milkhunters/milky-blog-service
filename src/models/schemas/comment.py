import uuid
from datetime import datetime

from pydantic import BaseModel

from src.models.schemas import UserSmall, Article
from src.models.state import CommentState


class Comment(BaseModel):
    id: uuid.UUID
    content: str
    owner: UserSmall
    nearest_ancestor_id: uuid.UUID
    article_id: uuid.UUID
    state: CommentState
    answers: list[dict] # todo: типы

    created_at: datetime
    updated_at: datetime = None

    class Config:
        orm_mode = True
        extra = 'ignore'


class CommentBranch(BaseModel):
    """
    Модель ветки комментария

    """
    ancestor_id: uuid.UUID
    descendant_id: uuid.UUID
    nearest_ancestor_id: uuid.UUID
    article: Article
    level: int

    created_at: datetime

    class Config:
        orm_mode = True
