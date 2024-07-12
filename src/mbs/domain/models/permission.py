from enum import StrEnum, auto


type PermissionTextId = str


class AutoName(StrEnum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class Permission(AutoName):
    CreateArticle = auto()
    GetArticle = auto()
    GetSelfArticle = auto()
    GetPublishedArticle = auto()
    UpdateArticle = auto()
    UpdateSelfArticle = auto()
    DeleteArticle = auto()
    DeleteSelfArticle = auto()
    RateArticle = auto()

    CreateComment = auto()
    GetComment = auto()
    GetPublishedComment = auto()
    UpdateComment = auto()
    UpdateSelfComment = auto()
    DeleteComment = auto()
    DeleteSelfComment = auto()

    CreateArticleFile = auto()
    ConfirmArticleFile = auto()
    GetArticleFile = auto()
    DeleteArticleFile = auto()

    GetTag = auto()
    GetTagStats = auto()
