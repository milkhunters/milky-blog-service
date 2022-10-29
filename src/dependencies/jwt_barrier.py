from fastapi import Request, Response

from models.state import UserStates
from fastapi.openapi.models import SecurityBase as SecurityBaseModel

from exceptions.api import APIError


class JWTCookie:
    model: SecurityBaseModel
    scheme_name: str

    def __init__(self, *, auto_error: bool = True):
        self.scheme_name = self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(self, request: Request, response: Response):
        if request.user.is_authenticated:
            if request.user.state == UserStates.blocked:
                if self.auto_error:
                    raise APIError(906)
                else:
                    return None
            elif request.user.state == UserStates.not_confirmed:
                if self.auto_error:
                    raise APIError(907)
                else:
                    return None
            return request.user
        if self.auto_error:
            raise APIError(908)
        else:
            return None
