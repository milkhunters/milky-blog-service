from enum import StrEnum, auto


class ArticleState(StrEnum):
    DRAFT = auto()
    PUBLISHED = auto()
    DELETED = auto()
