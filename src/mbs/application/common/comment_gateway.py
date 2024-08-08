from abc import abstractmethod
from typing import Protocol

from mbs.domain.models import Comment, CommentId, ArticleId, UserId, File, FileId


class CommentReader(Protocol):
    @abstractmethod
    async def get_comment(self, comment_id: CommentId) -> Comment | None:
        pass

    async def get_comment_with_files(self, comment_id: CommentId) -> tuple[Comment, list[File]] | None:
        pass

    @abstractmethod
    async def get_comments_with_files(self, article_id: ArticleId) -> list[tuple[Comment, int, list[File]]]:
        pass


class CommentWriter(Protocol):
    @abstractmethod
    async def save_comment(self, comment: Comment) -> None:
        pass


class CommentRemover(Protocol):

    @abstractmethod
    async def delete_article_comments(self, article_id: ArticleId) -> None:
        pass


class CommentRater(Protocol):
    @abstractmethod
    async def rate_comment(self, comment_id: CommentId, user_id: UserId) -> None:
        """
        Rate comment by user

        if user already rated comment, then remove rating
        """
        pass

    @abstractmethod
    async def is_comment_rated(self, comment_id: CommentId, user_id: UserId) -> bool:
        pass

    @abstractmethod
    async def is_comments_rated(self, comment_ids: list[CommentId], user_id: UserId) -> list[bool]:
        pass


class CommentFile(Protocol):
    @abstractmethod
    async def is_file_linked_to_comment(self, comment_id: CommentId, file_id: FileId) -> bool:
        pass

    @abstractmethod
    async def link_file_to_comment(self, comment_id: CommentId, file_id: FileId) -> None:
        pass

    @abstractmethod
    async def unlink_file_from_comment(self, comment_id: CommentId, file_id: FileId) -> None:
        pass
