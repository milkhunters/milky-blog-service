import dataclasses
from enum import Enum, unique
from abc import ABC, abstractmethod
from typing import Optional, Union, IO


@unique
class ContentType(Enum):
    """
    Типы контента
    """
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    IMAGE_GIF = "image/gif"
    IMAGE_BMP = "image/bmp"
    # TODO: добавить остальные типы/доработать

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


@dataclasses.dataclass
class File:
    id: str
    name: str
    content_type: ContentType
    size: Optional[int]
    bytes: Optional[bytes]
    owner_id: int


class AbstractStorage(ABC):
    """Abstract storage class"""

    @abstractmethod
    async def __aenter__(self, *args, **kwargs):
        pass

    @abstractmethod
    async def __aexit__(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get(self, file_id: str) -> Optional[File]:
        """
        Получить файл из хранилища
        :param file_id:
        :return:
        """
        pass

    @abstractmethod
    async def save(self, name: str, content_type: ContentType, file: Union[bytes, IO], owner_id: int) -> str:
        """
        Сохранить файл в хранилище
        :param owner_id:
        :param file:
        :param content_type: тип файла
        :param name: имя файла
        :return: file_id сохраненного файла
        """
        pass

    @abstractmethod
    async def delete(self, file_id: int) -> None:
        """
        Удалить файл из хранилища
        :param file_id:
        :return:
        """
        pass
