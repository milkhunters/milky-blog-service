import uuid
from datetime import datetime

from pydantic import BaseModel
from src.models.state import ArticleState
from .user import UserSmall


class ArticleTagItem(BaseModel):
    id: uuid.UUID
    title: str


class Article(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    poster_url: str = None
    tags: list[ArticleTagItem]
    state: ArticleState
    owner: UserSmall

    created_at: datetime
    updated_at: datetime = None

    class Config:
        orm_mode = True


class ArticleSmall(BaseModel):
    id: uuid.UUID
    title: str
    poster_url: str = None
    tags: list[ArticleTagItem]
    state: ArticleState
    owner: UserSmall

    created_at: datetime
    updated_at: datetime = None

    class Config:
        orm_mode = True


class ArticleCreate(BaseModel):
    title: str
    content: str
    state: ArticleState
    poster_url: str = None
    tags: list[str]


class ArticleUpdate(BaseModel):
    poster_url: str = None
    title: str = None
    content: str = None
    state: ArticleState = None
    tags: list[str] = None

    class Config:
        extra = 'ignore'
