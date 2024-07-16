from abc import abstractmethod
from typing import Protocol

from mbs.domain.models import File, FileId, UserId


class FileReader(Protocol):
    @abstractmethod
    async def get_file(self, file_id: FileId) -> File | None:
        pass


class FileWriter(Protocol):
    @abstractmethod
    async def save_file(self, file: File) -> None:
        pass


class FileRemover(Protocol):
    @abstractmethod
    async def remove_file(self, file_id: FileId) -> None:
        pass
