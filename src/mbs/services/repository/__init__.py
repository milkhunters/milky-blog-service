from .article import ArticleRepo
from .comment import CommentRepo, CommentTreeRepo
from .like import LikeRepo
from .notification import NotificationRepo
from .tag import TagRepo
from .file import FileRepo


class RepoFactory:
    def __init__(self, session):
        self._session = session

    @property
    def notification(self) -> NotificationRepo:
        return NotificationRepo(self._session)

    @property
    def article(self) -> ArticleRepo:
        return ArticleRepo(self._session)

    @property
    def comment(self) -> CommentRepo:
        return CommentRepo(self._session)

    @property
    def comment_tree(self) -> CommentTreeRepo:
        return CommentTreeRepo(self._session)

    @property
    def tag(self) -> TagRepo:
        return TagRepo(self._session)

    @property
    def like(self) -> LikeRepo:
        return LikeRepo(self._session)

    @property
    def file(self) -> FileRepo:
        return FileRepo(self._session)
