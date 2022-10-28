from enum import Enum, unique


@unique
class UserStates(Enum):
    not_confirmed = 0
    active = 1
    blocked = 2
    deleted = 3


@unique
class ArticleState(Enum):
    """
    Статус публикации
    не является pydantic моделью

    PS: было переписано с dataclass на enum
    """
    draft: int = 0
    published: int = 1
    archived: int = 2
    deleted: int = 3


@unique
class CommentState(Enum):
    """
    Статус комментария

    PS: было переписано с dataclass на enum
    """
    deleted: int = 0
    published: int = 1


@unique
class NotificationTypes(Enum):
    """
    Типы уведомлений

    PS: было переписано с dataclass на enum
    """
    comment_answer = 1
