from functools import wraps

from src.exceptions import AccessDenied
from src.models.role import Role


def role_filter(*roles: Role):
    """
    Role Filter decorator for ApplicationServices
    It is necessary that the class of the method being decorated has a field '_current_user'

    :param roles: user roles
    :return: decorator
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            service_class: object = args[0]
            current_user = service_class.__getattribute__('_current_user')
            if not current_user:
                raise ValueError('AuthMiddleware not found')

            if current_user.role in roles:
                return await func(*args, **kwargs)
            else:
                raise AccessDenied('У вас нет прав для выполнения этого действия')

        return wrapper

    return decorator
