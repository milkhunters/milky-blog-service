from abc import abstractmethod
from typing import Protocol

from mbs.domain.models import Tag, TagId, ArticleId


class TagReader(Protocol):
    @abstractmethod
    async def get_tag(self, tag_id: TagId) -> Tag:
        pass

    @abstractmethod
    async def find_tags(self, tags: list[str]) -> list[Tag]:
        pass

    @abstractmethod
    async def get_article_tags(self, article_id: ArticleId) -> list[Tag]:
        pass


class TagWriter(Protocol):
    @abstractmethod
    async def save_tags(self, tags: list[Tag]) -> None:
        pass


class TagLinker(Protocol):
    @abstractmethod
    async def link_tags(self, article_id: ArticleId, tags: list[TagId]) -> None:
        pass
