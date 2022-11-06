from datetime import datetime
from typing import Any, Optional, List

from pydantic import BaseModel, validator
from tortoise import fields

from .user import User
from models.state import ArticleState


class Article(BaseModel):
    """
    Базовая модель статьи

    """
    id: int
    title: str
    poster_url: Optional[str]
    state: ArticleState  # TODO: перейти на enum
    description: str
    content: str
    tags: Optional[list['Tag']]
    owner: User
    create_time: datetime
    update_time: Optional[datetime]

    @validator("*", pre=True, each_item=False)
    def _tortoise_convert(cls, value):
        # Computed fields
        if callable(value):
            return value()
        # Convert ManyToManyRelation to list
        if isinstance(value, (fields.ManyToManyRelation, fields.ReverseRelation)):
            return list(value)
        return value

    class Config:
        orm_mode = True


class Comment(BaseModel):
    """
    Базовая модель комментария
    """
    id: int
    content: str
    owner_id: int
    first_name: Optional[str]
    last_name: Optional[str]  # TODO:  Изменить на модель! !!
    username: str
    nearest_ancestor_id: Optional[int]
    article_id: int
    state: int  # TODO: перейти на enum
    answers: Optional[list[dict]]  # Todo проверить типы
    create_time: datetime
    update_time: Optional[datetime]

    class Config:
        orm_mode = True
        extra = 'ignore'


class CommentBranch(BaseModel):
    """
    Модель ветки комментария

    """
    ancestor_id: int
    descendant_id: int
    nearest_ancestor_id: int
    article: Article
    level: int
    create_time: datetime


class Tag(BaseModel):
    """
    Базовая модель тега

    """
    id: int
    name: str


class ArticleCreate(BaseModel):
    poster_url: Optional[str]
    title: str
    content: str
    state: ArticleState
    tags: list[str]


class ArticleUpdate(BaseModel):
    poster_url: Optional[str]
    title: Optional[str]
    content: Optional[str]
    state: Optional[ArticleState]
    tags: Optional[list[str]]

    class Config:
        extra = 'ignore'
