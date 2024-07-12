from enum import StrEnum, auto


class ArticleState(StrEnum):
    DRAFT = auto()
    PUBLISHED = auto()
    ARCHIVED = auto()
    DELETED = auto()