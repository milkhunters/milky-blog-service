from abc import abstractmethod
from typing import Protocol

from mbs.application.common.presigned_post_url import PreSignedPostUrl
from mbs.domain.models import FileId, ArticleId, CommentId


class StorageReader(Protocol):
    @abstractmethod
    async def is_exist_article_object(self, article_id: ArticleId, file_id: FileId) -> bool:
        pass

    @abstractmethod
    async def is_exist_comment_object(self, comment_id: CommentId, file_id: FileId) -> bool:
        pass


class StorageAccessLinkMaker(Protocol):
    @abstractmethod
    async def make_article_upload_link(
            self,
            article_id: ArticleId,
            file_id: FileId,
            content_type: str,
            content_length: tuple[int, int],
            expires_in: int
    ) -> PreSignedPostUrl:
        """
        article_id - идентификатор публикации
        file_id - идентификатор файла
        content_type - MIME-тип файла
        content_length - диапазон размера файла (минимальная и максимальная длина в байтах)
        expires_in - время жизни ссылки в секундах
        """
        pass

    @abstractmethod
    async def make_comment_upload_link(
            self,
            comment_id: CommentId,
            file_id: FileId,
            content_type: str,
            content_length: tuple[int, int],
            expires_in: int
    ) -> PreSignedPostUrl:
        """
        comment_id - идентификатор комментария
        file_id - идентификатор файла
        content_type - MIME-тип файла
        content_length - диапазон размера файла (минимальная и максимальная длина в мб)
        expires_in - время жизни ссылки в секундах
        """
        pass

    @abstractmethod
    async def make_article_download_link(
            self,
            article_id: ArticleId,
            file_id: FileId,
    ) -> str:
        pass

    @abstractmethod
    async def make_comment_download_link(
            self,
            comment_id: CommentId,
            file_id: FileId,
    ) -> str:
        pass



class StorageRemover(Protocol):
    @abstractmethod
    async def remove_article_object(self, article_id: ArticleId, file_id: FileId) -> None:
        pass

    @abstractmethod
    async def remove_comment_object(self, comment_id: str, file_id: FileId) -> None:
        pass
