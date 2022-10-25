from fastapi import Request

from exceptions.api import APIError
from models import Role


class MinRoleFilter:
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

    def __call__(self, request: Request) -> None:
        user_role: Role = request.user.role
        if user_role.value() >= self._role.value(): # todo после дополнения роли, исправить
            return

        if self._auto_error:
            raise APIError(909)
        else:
            return
