import dataclasses
import uuid
from abc import ABC, abstractmethod
from typing import IO


class AbstractStorage(ABC):
    """Abstract storage class"""

    @abstractmethod
    async def get(self, file_id: uuid.UUID):
        """
        Получить файл из хранилища
        :param file_id:
        :param load_bytes:
        :return:
        """
        pass

    @abstractmethod
    async def save(self, file_id: uuid.UUID, file: bytes | IO):
        """
        Сохранить файл в хранилище
        :param file:
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
