from enum import Enum


class UserStates(int, Enum):
    not_confirmed = 0
    active = 1
    blocked = 2
    deleted = 3


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
