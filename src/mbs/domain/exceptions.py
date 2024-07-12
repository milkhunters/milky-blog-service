
class DomainError(Exception):
    pass


class AuthenticationError(DomainError):
    pass


class AccessDenied(DomainError):
    pass


class ValidationError(DomainError):
    pass
