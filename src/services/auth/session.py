import uuid
from typing import Optional

from fastapi import Request, Response
from config import load_config
import utils

config = load_config()


class SessionManager:
    COOKIE_EXP = 31536000
    REDIS_EXP = 2592000
    COOKIE_PATH = "/api"
    COOKIE_DOMAIN = None
    COOKIE_SESSION_KEY = "session_id"

    def __init__(self):
        if not utils.RedisClient.redis_client:
            utils.RedisClient.open_redis_client()

    def get_session_id(self, request: Request) -> Optional[int]:
        """
        Выдает идентификатор сессии из куков

        :param request:
        :return: session_id
        """

        str_cookie_session_id = request.cookies.get(self.COOKIE_SESSION_KEY)
        try:
            cookie_session_id = int(str_cookie_session_id)
        except (ValueError, TypeError):
            return None
        return cookie_session_id

    async def set_session_id(
            self,
            response: Response,
            refresh_token: str,
            session_id: int = None
    ) -> int:
        """
        Генерирует и устанавливает сессию в redis и в куки

        :param response: 
        :param refresh_token: 
        :param session_id: 
        :return: session_id
        """
        if not session_id:
            session_id = uuid.uuid4().int
        response.set_cookie(
            key=self.COOKIE_SESSION_KEY,
            value=str(session_id),
            secure=config.is_secure_cookie,
            httponly=True,
            samesite="Strict",
            max_age=self.COOKIE_EXP,
            path=self.COOKIE_PATH
        )
        await utils.RedisClient.set(str(session_id), refresh_token, expire=self.REDIS_EXP)
        return session_id

    async def delete_session_id(self, session_id: int, response: Response) -> None:
        """
        Удаляет сессию из куков и из redis

        :param
        """
        await utils.RedisClient.delete(str(session_id))
        response.delete_cookie(
            key=self.COOKIE_SESSION_KEY,
            secure=config.is_secure_cookie,
            httponly=True,
            samesite="Strict",
            path=self.COOKIE_PATH
        )

    async def is_valid_session(self, session_id: int, cookie_refresh_token: str) -> bool:
        """
        Проверяет валидность сессии
        :param session_id:
        :param cookie_refresh_token:
        :return: True or False
        """
        redis_refresh_token = await utils.RedisClient.get(str(session_id))
        if not redis_refresh_token:
            return False
        if redis_refresh_token != cookie_refresh_token:
            return False
        return True
