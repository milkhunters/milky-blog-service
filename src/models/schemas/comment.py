import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

from src.models.schemas import UserSmall, Article
from src.models.state import CommentState


class Comment(BaseModel):
    id: uuid.UUID
    content: str
    owner: UserSmall
    state: CommentState

    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
        extra = 'ignore'


class CommentNode(Comment):
    """
    Модель комментария с деревом ответов

    """
    answers: list['CommentNode']
    parent_id: uuid.UUID | None
    level: int

    class Config:
        from_attributes = True


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
        from_attributes = True


class CommentCreate(BaseModel):
    content: str

    @field_validator('content')
    def content_must_be_valid(cls, value):
        if not value:
            raise ValueError("Комментарий не может быть пустым")

        if len(value) > 1000:
            raise ValueError("Комментарий не может быть длиннее 1000 символов")
        return value


class CommentUpdate(BaseModel):
    content: str

    @field_validator('content')
    def content_must_be_valid(cls, value):
        if not value:
            raise ValueError("Комментарий не может быть пустым")

        if len(value) > 1000:
            raise ValueError("Комментарий не может быть длиннее 1000 символов")
        return value
