import uuid
import datetime

from mbs.domain.exceptions import ValidationError
from mbs.domain.models import Article
from mbs.domain.models.article_state import ArticleState


class ValidatorService:

    def __init__(self):
        self.article_content_max_length = 32000
        self.article_title_max_length = 255
        self.article_title_min_length = 8
        self.article_content_min_length = 32

        self.comment_content_max_length = 1000
        self.comment_content_min_length = 8

        self.tag_title_max_length = 32
        self.tag_title_min_length = 3

        self.per_page_limit = 100


    def validate_article_title(self, title: str):
        if len(title) < self.article_title_min_length:
            raise ValidationError(f"Заголовок не может содержать меньше {self.article_title_min_length} символов")
        if len(title) > self.article_title_max_length:
            raise ValidationError(f"Заголовок не может содержать больше {self.article_title_max_length} символов")

    def validate_article_content(self, content: str):
        if len(content) < self.article_content_min_length:
            raise ValidationError(f"Публикация не может содержать меньше {self.article_content_min_length} символов")
        if len(content) > self.article_content_max_length:
            raise ValidationError(f"Публикация не может содержать больше {self.article_content_max_length} символов")

    def validate_comment_content(self, content: str):
        if len(content) < self.comment_content_min_length:
            raise ValidationError(f"Комментарий не может содержать меньше {self.comment_content_min_length} символов")
        if len(content) > self.comment_content_max_length:
            raise ValidationError(f"Комментарий не может содержать больше {self.comment_content_max_length} символов")

    def validate_tag_title(self, title: str):
        if len(title) < self.tag_title_min_length:
            raise ValidationError(f"Тег не может содержать меньше {self.tag_title_min_length} символов")
        if len(title) > self.tag_title_max_length:
            raise ValidationError(f"Тег не может содержать больше {self.tag_title_max_length} символов")

    def validate_pagination(self, page: int, per_page: int):
        if page < 1:
            raise ValidationError("Номер страницы не может быть меньше 1")
        if page > 2147483646:
            raise ValidationError("Номер страницы не может быть больше 2^32")

        if per_page < 1:
            raise ValidationError("Неверное количество элементов на странице")
        if per_page > self.per_page_limit:
            raise ValidationError(f"Количество элементов на странице не может быть больше {self.per_page_limit}")
