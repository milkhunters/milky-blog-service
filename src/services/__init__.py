import aio_pika

from src.models.auth import BaseUser
from . import repository
from . import auth
from .article import ArticleApplicationService
from .auth import AuthApplicationService
from .comment import CommentApplicationService
from .email import EmailService
from .notification import NotificationApplicationService
from .stats import StatsApplicationService
from .user import UserApplicationService


class ServiceFactory:
    def __init__(
            self,
            repo_factory: repository.RepoFactory,
            *,
            current_user: BaseUser,
            config,
            redis_client,
            rmq: aio_pika.RobustConnection,
    ):
        self._repo = repo_factory
        self._current_user = current_user
        self._config = config
        self._redis_client = redis_client
        self._rmq = rmq

    @property
    def user(self) -> UserApplicationService:
        return UserApplicationService(self._current_user, user_repo=self._repo.user)

    @property
    def auth(self) -> AuthApplicationService:
        return AuthApplicationService(
            self._current_user,
            jwt_manager=auth.JWTManager(config=self._config),
            session_manager=auth.SessionManager(redis_client=self._redis_client, config=self._config),
            user_repo=self._repo.user,
            redis_client=self._redis_client,
            email_service=self.email,
        )

    @property
    def article(self) -> ArticleApplicationService:
        return ArticleApplicationService(
            self._current_user,
            article_repo=self._repo.article,
            tag_repo=self._repo.tag,
            comment_repo=self._repo.comment,
            comment_tree_repo=self._repo.comment_tree,
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
    def email(self) -> EmailService:
        return EmailService(config=self._config.EMAIL, rmq=self._rmq)

    @property
    def stats(self) -> StatsApplicationService:
        return StatsApplicationService(redis_client=self._redis_client, config=self._config)
