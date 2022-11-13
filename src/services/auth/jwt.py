import time
from typing import Optional

from jose import jwt, JWTError
from pydantic import ValidationError
from fastapi import Response, Request

from config import load_config
from models import schemas

config = load_config()


class JWTManager:
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
    REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
    JWT_ACCESS_SECRET_KEY = config.base.jwt.JWT_ACCESS_SECRET_KEY
    JWT_REFRESH_SECRET_KEY = config.base.jwt.JWT_REFRESH_SECRET_KEY

    COOKIE_EXP = 31536000
    COOKIE_PATH = "/api"
    COOKIE_DOMAIN = None
    COOKIE_ACCESS_KEY = "access_token"
    COOKIE_REFRESH_KEY = "refresh_token"

    def is_valid_refresh_token(self, token: str) -> bool:
        """
        Проверяет refresh-токен на валидность
        :param token:
        :return:
        """
        return self._is_valid_jwt(token, self.JWT_REFRESH_SECRET_KEY)

    def is_valid_access_token(self, token: str) -> bool:
        """
        Проверяет access-токен на валидность
        :param token:
        :return:
        """
        return self._is_valid_jwt(token, self.JWT_ACCESS_SECRET_KEY)

    def decode_access_token(self, token: str) -> schemas.TokenPayload:
        """
        Декодирует access-токен (получает payload)
        :param token:
        :return:
        """
        return self._decode_jwt(token, self.JWT_ACCESS_SECRET_KEY)

    def decode_refresh_token(self, token: str) -> schemas.TokenPayload:
        """
        Декодирует refresh-токен (получает payload)
        :param token:
        :return:
        """
        return self._decode_jwt(token, self.JWT_REFRESH_SECRET_KEY)

    def generate_access_token(self, id: int, username: str, role_id: int, state_id: int, **kwargs) -> str:
        """
        Генерирует access-токен
        на основе payload:
        :param id: ид пользователя
        :param username: имя пользователя
        :param role_id: ид роли
        :param state_id: ид состояния
        :param kwargs:
        :return:
        """
        return self._generate_token(
            id,
            username,
            role_id,
            state_id,
            exp_minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES,
            secret_key=self.JWT_ACCESS_SECRET_KEY
        )

    def generate_refresh_token(self, id: int, username: str, role_id: int, state_id: int, **kwargs) -> str:
        """
        Генерирует refresh-токен
        на основе payload:
        :param id: ид пользователя
        :param username: имя пользователя
        :param role_id: ид роли
        :param state_id: ид состояния
        :param kwargs:
        :return:
        """
        return self._generate_token(
            id,
            username,
            role_id,
            state_id,
            exp_minutes=self.REFRESH_TOKEN_EXPIRE_MINUTES,
            secret_key=self.JWT_REFRESH_SECRET_KEY
        )

    def set_jwt_cookie(self, response: Response, tokens: schemas.Tokens) -> None:
        """
        Устанавливает в куки access- и refresh-токены
        :param response:
        :param tokens:
        :return:
        """
        response.set_cookie(
            key=self.COOKIE_ACCESS_KEY,
            value=tokens.access_token,
            secure=config.is_secure_cookie,
            httponly=True,
            samesite="strict",
            max_age=self.COOKIE_EXP,
            path=self.COOKIE_PATH,
            domain=self.COOKIE_DOMAIN
        )
        response.set_cookie(
            key=self.COOKIE_REFRESH_KEY,
            value=tokens.refresh_token,
            secure=config.is_secure_cookie,
            httponly=True,
            samesite="strict",
            max_age=self.COOKIE_EXP,
            path=self.COOKIE_PATH,
            domain=self.COOKIE_DOMAIN
        )

    def get_jwt_cookie(self, request: Request) -> Optional[schemas.Tokens]:
        """
        Получает из кук access и refresh-токены
        :param request:
        :return:
        """
        access_token = request.cookies.get(self.COOKIE_ACCESS_KEY)
        refresh_token = request.cookies.get(self.COOKIE_REFRESH_KEY)
        if not access_token or not refresh_token:
            return None
        return schemas.Tokens(access_token=access_token, refresh_token=refresh_token)

    def delete_jwt_cookie(self, response: Response) -> None:
        """
        Удаляет из кук access и refresh-токены
        :param response:
        :return:
        """
        tokens = schemas.Tokens(access_token="", refresh_token="")
        self.set_jwt_cookie(response, tokens)

    def _is_valid_jwt(self, token: str, secret_key: str) -> bool:
        try:
            payload = self._decode_jwt(token, secret_key)
        except JWTError:
            return False
        except ValidationError:
            return False

        if payload.exp < int(time.time()):
            return False
        return True

    def _generate_token(
            self,
            user_id: int,
            username: str,
            role_id: int,
            state_id: int,
            exp_minutes: int,
            secret_key: str
    ) -> str:
        payload = schemas.TokenPayload(
            id=user_id,
            username=username,
            role_id=role_id,
            state_id=state_id,
            exp=int(time.time() + exp_minutes * 60)
        )
        return jwt.encode(payload.dict(), secret_key, self.ALGORITHM)

    def _decode_jwt(self, token: str, secret_key: str) -> schemas.TokenPayload:
        return schemas.TokenPayload.parse_obj(jwt.decode(token, secret_key, algorithms=[self.ALGORITHM]))
