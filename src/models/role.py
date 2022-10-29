from enum import Enum, unique
from typing import Tuple


@unique
class MainRole(Enum):
    user = 1
    moderator = 2
    administrator = 3


@unique
class AdditionalRole(Enum):
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5
    six = 6
    seven = 7
    eight = 8
    nine = 9


class Role:
    """
    Класс для работы с ролями пользователей

    Принимает на вход два параметра:
    - main_role: enum MainRole
    - additional_role: enum AdditionalRole
    Может вернуть как int, так и tuple из  двух
    переданных параметров

    Пример использования:

    >>> Role(MainRole.user, AdditionalRole.one)

    >>> 11

    :param main_role:
    :param additional_role:

    todo: описать все операции, как если бы они выполнялись от int
        например: SomeRole >= SomeSomeRole
    """
    def __init__(self, main_role: MainRole, additional_role: AdditionalRole):
        self.main_role = main_role
        self.additional_role = additional_role

    def value(self) -> int:
        return int(f"{self.main_role.value}{self.additional_role.value}")

    def to_int(self):
        return int(self)

    def to_tuple(self) -> Tuple[MainRole, AdditionalRole]:
        return self.main_role, self.additional_role

    def __int__(self) -> int:
        return self.value()

    def __repr__(self):
        return f"{self.main_role.name} {self.additional_role.name}"

    def __eq__(self, other):
        return self.value() == other.value()

    @classmethod
    def from_int(cls, value: int):
        """
        Преобразует целое число в класс Role
        :param value:

        :return: self
        """
        if value not in range(10, 40):
            raise ValueError("Значение роли должно быть в диапазоне 10-39")

        main_role = value // 10
        additional_role = value % 10
        return cls(MainRole(main_role), AdditionalRole(additional_role))
