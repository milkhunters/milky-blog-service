import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator
from src.models.state import ArticleState


class ArticleTagItem(BaseModel):
    id: uuid.UUID
    title: str

    class Config:
        from_attributes = True


class Article(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    poster_url: str | None
    views: int
    likes_count: int
    tags: list[ArticleTagItem]
    state: ArticleState
    owner_id: uuid.UUID

    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class ArticleSmall(BaseModel):
    id: uuid.UUID
    title: str
    poster_url: str | None
    views: int
    likes_count: int
    tags: list[ArticleTagItem]
    state: ArticleState
    owner_id: uuid.UUID

    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class ArticleCreate(BaseModel):
    title: str
    content: str
    state: ArticleState
    poster_url: str = None
    tags: list[str]

    @field_validator('content')
    def content_must_be_valid(cls, value):
        if not value:
            raise ValueError("Публикация не может быть пустой")

        if len(value) > 32000:
            raise ValueError("Публикация не может быть длиннее 32000 символов")
        return value

    @field_validator('title')
    def title_must_be_valid(cls, value):
        if not value:
            raise ValueError("Заголовок не может быть пустым")

        if len(value) > 255:
            raise ValueError("Заголовок не может быть длиннее 255 символов")
        return value

    @field_validator('poster_url')
    def poster_url_must_be_valid(cls, value):
        if value and len(value) > 255:
            raise ValueError("Ссылка на постер не может быть длиннее 255 символов")
        return value

    @field_validator('tags')
    def tags_must_be_valid(cls, value):
        for tag in value:
            if len(tag) > 32:
                raise ValueError("Тег не может быть длиннее 32 символов")
        return value


class ArticleUpdate(BaseModel):
    poster_url: str = None
    title: str = None
    content: str = None
    state: ArticleState = None
    tags: list[str] = None

    class Config:
        extra = 'ignore'

    @field_validator('content')
    def content_must_be_valid(cls, value):
        if value and len(value) > 32000:
            raise ValueError("Публикация не может быть длиннее 32000 символов")
        return value

    @field_validator('title')
    def title_must_be_valid(cls, value):
        if value and len(value) > 255:
            raise ValueError("Заголовок не может быть длиннее 255 символов")
        return value

    @field_validator('poster_url')
    def poster_url_must_be_valid(cls, value):
        if value and len(value) > 255:
            raise ValueError("Ссылка на постер не может быть длиннее 255 символов")
        return value

    @field_validator('tags')
    def tags_must_be_valid(cls, value):
        for tag in value:
            if len(tag) > 32:
                raise ValueError("Тег не может быть длиннее 32 символов")
        return value
