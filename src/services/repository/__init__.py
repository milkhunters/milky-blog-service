from .comment import CommentRepo, CommentTreeRepo
from .file import FileRepo
from .notification import NotificationRepo
from .user import UserRepo


class RepoFactory:
    def __init__(self, session):
        self._session = session

    @property
    def user(self) -> UserRepo:
        return UserRepo(self._session)

    @property
    def notification(self) -> NotificationRepo:
        return NotificationRepo(self._session)

    @property
    def comment(self) -> CommentRepo:
        return CommentRepo(self._session)

    @property
    def comment_tree(self) -> CommentTreeRepo:
        return CommentTreeRepo(self._session)

    @property
    def file(self) -> FileRepo:
        return FileRepo(self._session)
