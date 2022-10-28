from datetime import datetime
from typing import Any, Optional, List

import pydantic
from pydantic import BaseModel
from tortoise import fields

from .pagination import PaginationPage
from .user import UserOut


# Comments

class CommentOut(BaseModel):
    id: int
    content: str
    owner_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: str
    nearest_ancestor_id: Optional[int]
    article_id: int
    state: int
    answers: Optional[list[dict]]
    create_time: datetime
    update_time: datetime = None

    class Config:
        orm_mode = True
        extra = 'ignore'


# Tags

class TagOut(BaseModel):
    id: int
    name: str


# Articles

class ArticleCreate(BaseModel):
    """
    Входные данные для создания статьи

    """
    # todo: poster_url, когда Горох определится
    title: str
    content: str
    state: int
    tags: list[str]


class ArticleUpdate(BaseModel):
    """
    Входные данные для обновления статьи

    """
    # todo: poster_url, когда Горох определится
    title: Optional[str]
    content: Optional[str]
    state: Optional[int]
    tags: Optional[list[str]]

    class Config:
        extra = 'ignore'


class ArticleOut(BaseModel):
    """
    Используется для получения всех
    данных публикации

    """
    id: int
    title: str
    poster_url: str = None
    state: int
    description: str
    content: str
    tags: Optional[list[TagOut]]
    owner: UserOut
    create_time: datetime
    update_time: datetime

    @pydantic.validator("*", pre=True, each_item=False)
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


class ArticleOutMenu(BaseModel):
    """
    Используется для вывода списка статей,
    когда клиент получает несколько публикаций
    за раз, например, для формирования меню
    (Не включается полный контент)

    """
    id: int
    title: str
    poster_url: str = None
    state: int
    description: str
    tags: Optional[list[TagOut]]
    owner: UserOut
    create_time: datetime
    update_time: datetime

    @pydantic.validator("*", pre=True, each_item=False)
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


class ArticlesOutMenu(PaginationPage):
    """
        Несколько статей

        """
    items: Optional[list[ArticleOutMenu]]