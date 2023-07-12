from enum import Enum


class UserStates(int, Enum):
    NOT_CONFIRMED = 0
    ACTIVE = 1
    BLOCKED = 2
    DELETED = 3


class ArticleState(int, Enum):
    DRAFT = 0
    PUBLISHED = 1
    ARCHIVED = 2
    DELETED = 3


class CommentState(int, Enum):
    DELETED = 0
    PUBLISHED = 1


class NotificationTypes(int, Enum):
    COMMENT_ANSWER = 1
