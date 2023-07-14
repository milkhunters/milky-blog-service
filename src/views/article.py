from .base import BaseView
from src.models import schemas


class ArticleResponse(BaseView):
    content: schemas.Article


class ArticlesResponse(BaseView):
    content: list[schemas.Article]

