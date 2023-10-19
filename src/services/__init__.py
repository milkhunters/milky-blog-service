from src.models.auth import BaseUser
from . import auth
from . import repository
from .article import ArticleApplicationService
from .comment import CommentApplicationService
from .notification import NotificationApplicationService
from .permission import PermissionApplicationService
from .stats import StatsApplicationService


class ServiceFactory:
    def __init__(
            self,
            repo_factory: repository.RepoFactory,
            *,
            current_user: BaseUser,
            config,
            file_storage,
    ):
        self._repo = repo_factory
        self._current_user = current_user
        self._config = config
        self._file_storage = file_storage

    @property
    def article(self) -> ArticleApplicationService:
        return ArticleApplicationService(
            self._current_user,
            article_repo=self._repo.article,
            tag_repo=self._repo.tag,
            comment_repo=self._repo.comment,
            comment_tree_repo=self._repo.comment_tree,
            like_repo=self._repo.like,
            file_repo=self._repo.file,
            file_storage=self._file_storage,
        )

    @property
    def comment(self) -> CommentApplicationService:
        return CommentApplicationService(
            self._current_user,
            comment_repo=self._repo.comment,
            comment_tree_repo=self._repo.comment_tree,
            notify_repo=self._repo.notification,
            article_repo=self._repo.article
        )

    @property
    def notification(self) -> NotificationApplicationService:
        return NotificationApplicationService(self._current_user, notify_repo=self._repo.notification)

    @property
    def stats(self) -> StatsApplicationService:
        return StatsApplicationService(config=self._config)

    @property
    def permission(self) -> PermissionApplicationService:
        return PermissionApplicationService()
