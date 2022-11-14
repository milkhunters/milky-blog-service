from enum import Enum, unique


@unique
class UserStates(int, Enum):
    not_confirmed = 0
    active = 1
    blocked = 2
    deleted = 3


@unique
class ArticleState(int, Enum):
    """
    Статус публикации
    не является pydantic моделью

    PS: было переписано с dataclass на enum
    """
    DRAFT: int = 0
    PUBLISHED: int = 1
    ARCHIVED: int = 2
    DELETED: int = 3


@unique
class CommentState(int, Enum):
    """
    Статус комментария

    PS: было переписано с dataclass на enum
    """
    deleted: int = 0
    published: int = 1


@unique
class NotificationTypes(int, Enum):
    """
    Типы уведомлений

    PS: было переписано с dataclass на enum
    """
    comment_answer = 1
