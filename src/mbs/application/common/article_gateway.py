from abc import abstractmethod
from typing import Protocol

from mbs.domain.models import Article, ArticleId, ArticleState, UserId, File, FileId


class ArticleReader(Protocol):
    @abstractmethod
    async def get_article(self, article_id: ArticleId) -> Article | None:
        pass

    @abstractmethod
    async def get_articles(
            self,
            limit: int,
            offset: int,
            order_by: str,
            state: ArticleState,
            tag: str = None,
            query: str = None,
            author_id: UserId = None,
    ) -> list[Article]:
        pass


class ArticleWriter(Protocol):
    @abstractmethod
    async def save_article(self, article: Article) -> None:
        pass


class ArticleRater(Protocol):
    @abstractmethod
    async def rate_article(self, article_id: ArticleId, user_id: UserId) -> None:
        """
        Rate article by user

        if user already rated article, then remove rating
        """
        pass

    @abstractmethod
    async def is_article_rated(self, article_id: ArticleId, user_id: UserId) -> bool:
        pass

    @abstractmethod
    async def is_articles_rated(self, article_ids: list[ArticleId], user_id: UserId) -> list[bool]:
        pass


class ArticleFile(Protocol):
    @abstractmethod
    async def get_article_files(self, article_id: ArticleId) -> list[File]:
        pass

    @abstractmethod
    async def is_file_linked_to_article(self, article_id: ArticleId, file_id: FileId) -> bool:
        pass

    @abstractmethod
    async def link_file_to_article(self, article_id: ArticleId, file_id: FileId) -> None:
        pass

    @abstractmethod
    async def unlink_file_from_article(self, article_id: ArticleId, file_id: FileId) -> None:
        pass


class ArticleRemover(Protocol):
    @abstractmethod
    async def remove_article(self, article_id: ArticleId) -> None:
        pass
