
type MapError = dict[str, str]


class ApplicationError(Exception):
    def __init__(self, message: str | MapError, code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code


class InvalidData(ApplicationError):
    def __init__(self, message: str | MapError = "Неверные данные"):
        super().__init__(message, 400)


class NotFound(ApplicationError):
    def __init__(self, message: str | MapError = "Не найдено"):
        super().__init__(message, 404)


class Unauthorized(ApplicationError):
    def __init__(self, message: str | MapError = "Необходима авторизация"):
        super().__init__(message, 401)


class Forbidden(ApplicationError):
    def __init__(self, message: str | MapError = "Доступ запрещен"):
        super().__init__(message, 403)
