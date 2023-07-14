import dataclasses
import uuid
from abc import ABC, abstractmethod
from typing import IO


@dataclasses.dataclass
class File:
    id: uuid.UUID
    title: str
    content_type: any
    bytes: any
    owner_id: any
    size: int = None


class AbstractStorage(ABC):
    """Abstract storage class"""

    @abstractmethod
    async def __aenter__(self, *args, **kwargs):
        pass

    @abstractmethod
    async def __aexit__(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get(self, file_id: uuid.UUID, load_bytes: bool = False) -> File | None:
        """
        Получить файл из хранилища
        :param file_id:
        :param load_bytes:
        :return:
        """
        pass

    @abstractmethod
    async def save(self, file_id: uuid.UUID, title: str, content_type: any, file: bytes | IO, owner_id: any):
        """
        Сохранить файл в хранилище
        :param owner_id:
        :param file:
        :param content_type: тип файла
        :param title: имя файла
        :param file_id
        """
        pass

    @abstractmethod
    async def delete(self, file_id: uuid.UUID) -> None:
        """
        Удалить файл из хранилища
        :param file_id:
        :return:
        """
        pass
