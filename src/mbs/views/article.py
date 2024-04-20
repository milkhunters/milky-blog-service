from .base import BaseView
from ..models import schemas


class ArticleResponse(BaseView):
    content: schemas.Article


class ArticlesResponse(BaseView):
    content: list[schemas.ArticleSmall]


class ArticleFilesResponse(BaseView):
    content: list[schemas.ArticleFileItem]


class ArticleFileResponse(BaseView):
    content: schemas.ArticleFileItem


class ArticleFileUploadResponse(BaseView):
    content: schemas.ArticleFileUpload
