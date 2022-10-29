from typing import Optional

from fastapi import Request

from exceptions.api import APIError
from models import Role


class RoleFilter:
    """
    Зависимость должна быть использована
    только в авторизованном пространстве

    """

    def __init__(self, role: Role, auto_error: bool = True):
        """

        Фильтрует пользователей по минимальному уровню доступа

        :param role: Роль пользователя
        :param args:
        """
        self._role: Role = role
        self._auto_error = auto_error

    def __call__(self, request: Request) -> Optional[bool]:
        user_role: Role = request.user.role
        if user_role.value() >= self._role.value():
            return True

        if self._auto_error:
            raise APIError(909)
        else:
            return
