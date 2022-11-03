from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator
from tortoise import fields

from models.schemas import BasePaginationModel
from models.schemas import Tag, User
from models.state import ArticleState


class ArticleResponse(BaseModel):
    """
    Используется для вывода списка статей,
    когда клиент получает несколько публикаций
    за раз, например, для формирования меню
    (Не включается полный контент)

    """
    id: int
    title: str
    poster_url: Optional[str]
    state: ArticleState
    description: str
    tags: Optional[list[Tag]]
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


class ArticlesResponse(BasePaginationModel):
    """
    Используется для вывода списка статей
    """
    items: Optional[list[ArticleResponse]]
