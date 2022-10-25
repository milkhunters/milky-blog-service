from enum import Enum, unique


@unique
class UserStates(Enum):
    not_confirmed = 0
    active = 1
    blocked = 2
    deleted = 3
