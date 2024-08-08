from abc import abstractmethod
from typing import Protocol

from mbs.domain.models import UserState, UserId, PermissionTextId


class IdProvider(Protocol):
    @abstractmethod
    def user_id(self) -> UserId:
        pass

    @abstractmethod
    def user_state(self) -> UserState:
        pass

    @abstractmethod
    def permissions(self) -> list[PermissionTextId]:
        pass

    @abstractmethod
    def is_auth(self) -> bool:
        pass
