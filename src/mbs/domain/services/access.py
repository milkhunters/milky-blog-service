from mbs.domain.exceptions import AuthenticationError, AccessDenied
from mbs.domain.models import (
    ArticleState,
    PermissionTextId,
    Permission,
    UserState,
    UserId
)


class AccessService:

    def ensure_can_create_article(
            self,
            is_auth: bool,
            permissions: list[PermissionTextId],
            user_state: UserState | None
    ):
        if not is_auth:
            raise AuthenticationError()

        if user_state != UserState.ACTIVE:
            raise AccessDenied()

        if Permission.CreateArticle not in permissions:
            raise AccessDenied()

    def ensure_can_update_article(
            self,
            is_auth: bool,
            user_id: UserId,
            article_author_id: UserId,
            permissions: list[PermissionTextId],
            user_state: UserState | None
    ):
        if not is_auth:
            raise AuthenticationError()

        if user_state != UserState.ACTIVE:
            raise AccessDenied()

        if user_id == article_author_id and Permission.UpdateSelfArticle in permissions:
            return

        if Permission.UpdateArticle in permissions:
            return

        raise AccessDenied()

    def ensure_can_delete_article(
            self,
            is_auth: bool,
            user_id: UserId,
            article_author_id: UserId,
            permissions: list[PermissionTextId],
            user_state: UserState | None
    ):
        if not is_auth:
            raise AuthenticationError()

        if user_state != UserState.ACTIVE:
            raise AccessDenied()

        if user_id == article_author_id and Permission.DeleteSelfArticle in permissions:
            return

        if Permission.DeleteArticle in permissions:
            return

        raise AccessDenied()

    def ensure_can_get_article(
            self,
            is_auth: bool,
            user_id: UserId,
            article_state: ArticleState,
            article_author_id: UserId,
            permissions: list[PermissionTextId],
            user_state: UserState | None
    ):
        if not is_auth:
            if (
                    (article_state == ArticleState.PUBLISHED and
                     Permission.GetPublishedArticle in permissions) or
                    Permission.GetArticle in permissions
            ):
                return
            raise AccessDenied()

        if user_state != UserState.ACTIVE:
            raise AccessDenied()

        if Permission.GetArticle in permissions:
            return

        if user_id == article_author_id and Permission.GetSelfArticle in permissions:
            return

        if article_state == ArticleState.PUBLISHED and Permission.GetPublishedArticle in permissions:
            return

        raise AccessDenied()

    def ensure_can_rate_article(
            self,
            is_auth: bool,
            permissions: list[PermissionTextId],
            user_state: UserState | None
    ):
        if not is_auth:
            raise AuthenticationError()

        if user_state != UserState.ACTIVE:
            raise AccessDenied()

        if Permission.RateArticle not in permissions:
            raise AccessDenied()

    def ensure_can_create_comment(
            self,
            is_auth: bool,
            permissions: list[PermissionTextId],
            user_state: UserState | None
    ):
        if not is_auth:
            raise AuthenticationError()

        if user_state != UserState.ACTIVE:
            raise AccessDenied()

        if Permission.CreateComment not in permissions:
            raise AccessDenied()

    def ensure_can_update_comment(
            self,
            is_auth: bool,
            user_id: UserId,
            comment_author_id: UserId,
            permissions: list[PermissionTextId],
            user_state: UserState | None
    ):
        if not is_auth:
            raise AuthenticationError()

        if user_state != UserState.ACTIVE:
            raise AccessDenied()

        if user_id == comment_author_id and Permission.UpdateSelfComment in permissions:
            return

        if Permission.UpdateComment in permissions:
            return

        raise AccessDenied()

    def ensure_can_delete_comment(
            self,
            is_auth: bool,
            user_id: UserId,
            comment_author_id: UserId,
            permissions: list[PermissionTextId],
            user_state: UserState | None
    ):
        if not is_auth:
            raise AuthenticationError()

        if user_state != UserState.ACTIVE:
            raise AccessDenied()

        if user_id == comment_author_id and Permission.DeleteSelfComment in permissions:
            return

        if Permission.DeleteComment in permissions:
            return

        raise AccessDenied()

    def ensure_can_get_comment(
            self,
            is_auth: bool,
            permissions: list[PermissionTextId],
            user_state: UserState | None
    ):
        if not is_auth:
            raise AuthenticationError()

        if user_state != UserState.ACTIVE:
            raise AccessDenied()

        if Permission.GetComment not in permissions:
            raise AccessDenied()


    def ensure_can_get_published_comment(
            self,
            permissions: list[PermissionTextId]
    ):
        if Permission.GetPublishedComment in permissions:
            return

        if Permission.GetComment in permissions:
            return

        raise AccessDenied()

    def ensure_can_create_article_file(
            self,
            is_auth: bool,
            permissions: list[PermissionTextId],
            user_state: UserState | None
    ):
        if not is_auth:
            raise AuthenticationError()

        if user_state != UserState.ACTIVE:
            raise AccessDenied()

        if Permission.CreateArticleFile not in permissions:
            raise AccessDenied()

    def ensure_can_confirm_article_file(
            self,
            is_auth: bool,
            permissions: list[PermissionTextId],
            user_state: UserState | None
    ):
        if not is_auth:
            raise AuthenticationError()

        if user_state != UserState.ACTIVE:
            raise AccessDenied()

        if Permission.ConfirmArticleFile not in permissions:
            raise AccessDenied()

    def ensure_can_get_article_file(
            self,
            is_auth: bool,
            permissions: list[PermissionTextId],
            user_state: UserState | None
    ):
        if not is_auth:
            raise AuthenticationError()

        if user_state != UserState.ACTIVE:
            raise AccessDenied()

        if Permission.GetArticleFile not in permissions:
            raise AccessDenied()

    def ensure_can_delete_article_file(
            self,
            is_auth: bool,
            permissions: list[PermissionTextId],
            user_state: UserState | None
    ):
        if not is_auth:
            raise AuthenticationError()

        if user_state != UserState.ACTIVE:
            raise AccessDenied()

        if Permission.DeleteArticleFile not in permissions:
            raise AccessDenied()

    def ensure_can_get_tag(
            self,
            permissions: list[PermissionTextId]
    ):
        if Permission.GetTag in permissions:
            return

        raise AccessDenied()
