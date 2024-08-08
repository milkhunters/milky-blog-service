import re

from mbs.domain.exceptions import ValidationError


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

        self.filename_max_length = 255

        self.mime_type_max_length = 255  # RFC 4288 and RFC 6838
        self.mime_type_regex = re.compile(r"\w+/[-+.\w]+")

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

    def validate_filename(self, filename: str):
        if len(filename) > self.filename_max_length:
            raise ValidationError(f"Имя файла не может содержать больше {self.filename_max_length} символов")

    def validate_mime_content_type(self, content_type: str):
        if len(content_type) > self.mime_type_max_length:
            raise ValidationError(f"Тип содержимого не может содержать больше {self.mime_type_max_length} символов")
        if not self.mime_type_regex.match(content_type):
            raise ValidationError("Неверный тип содержимого")
