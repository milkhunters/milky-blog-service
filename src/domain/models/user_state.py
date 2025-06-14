from enum import StrEnum, auto


class UserState(StrEnum):
    ACTIVE = auto()
    INACTIVE = auto()
    BANNED = auto()
    DELETED = auto()
