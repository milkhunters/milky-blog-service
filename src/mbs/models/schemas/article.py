import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

from mbs.models.file_type import FileType
from mbs.models.schemas.s3 import PreSignedPostUrl
from src import ArticleState


class ArticleTagItem(BaseModel):
    id: uuid.UUID
    title: str

    class Config:
        from_attributes = True


class Article(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    poster: uuid.UUID | None
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
    poster: uuid.UUID | None
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
    tags: list[str]

    @field_validator('content')
    def content_must_be_valid(cls, value):
        if not value:
            raise ValueError("Публикация не может быть пустой")

        if len(value) > 32000:
            raise ValueError("Публикация не может содержать более 32000 символов")
        return value

    @field_validator('title')
    def title_must_be_valid(cls, value):
        if not value:
            raise ValueError("Заголовок не может быть пустым")

        if len(value) > 255:
            raise ValueError("Заголовок не может содержать больше 255 символов")
        return value

    @field_validator('tags')
    def tags_must_be_valid(cls, value):
        for tag in value:
            if len(tag) > 32:
                raise ValueError("Тег не может содержать больше 32 символов")
        return value


class ArticleUpdate(BaseModel):
    title: str = None
    content: str = None
    state: ArticleState = None
    tags: list[str] = None

    class Config:
        extra = 'ignore'

    @field_validator('content')
    def content_must_be_valid(cls, value):
        if value and len(value) > 32000:
            raise ValueError("Публикация не может содержать больше 32000 символов")
        return value

    @field_validator('title')
    def title_must_be_valid(cls, value):
        if value and len(value) > 255:
            raise ValueError("Заголовок не может содержать больше 255 символов")
        return value

    @field_validator('tags')
    def tags_must_be_valid(cls, value):
        for tag in value:
            if len(tag) > 32:
                raise ValueError("Тег не может содержать больше 32 символов")
        return value


class ArticleFile(BaseModel):
    id: uuid.UUID
    filename: str
    article_id: uuid.UUID
    content_type: str
    is_uploaded: bool

    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class ArticleFileItem(BaseModel):
    id: uuid.UUID
    filename: str
    content_type: str
    url: str

    created_at: datetime
    updated_at: datetime | None


class ArticleFileCreate(BaseModel):
    filename: str
    content_type: FileType


class ArticleFileUpload(BaseModel):
    file_id: uuid.UUID
    upload_url: PreSignedPostUrl
