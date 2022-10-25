"""Application implementation - custom FastAPI HTTP exception with handler."""
from typing import Any, Optional, Dict

from fastapi import Request
from fastapi.responses import JSONResponse


class HTTPException(Exception):
    """Определите пользовательское определение класса HTTPException.
     Это исключение в сочетании с методом exception_handler позволяет вам использовать его
     так же, как вы использовали бы FastAPI.HTTPException с одним отличием.

     Вы имеете свободу определять тело возвращаемого ответа, тогда как
     содержимое FastAPI.HTTPException возвращается в ключе JSON "detail".

     FastAPI.HTTPException source:
      https://github.com/tiangolo/fastapi/blob/master/fastapi/exceptions.py
    """

    def __init__(
        self,
        status_code: int,
        content: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.status_code = status_code
        self.content = content
        self.headers = headers

    def __repr__(self):
        kwargs = []

        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                kwargs.append(
                    "{key}={value}".format(key=key, value=repr(value))
                )

        return "{name}({kwargs})".format(
            name=self.__class__.__name__, kwargs=", ".join(kwargs)
        )


async def http_exception_handler(request: Request, exception: HTTPException):
    """Определяет собственный обработчик HTTPException.
     В этом приложении настраиваемый обработчик добавляется в asgi.py при инициализации.
     Приложение FastAPI. Это необходимо для обработки пользовательского HTTException.
     глобально.

     Подробнее:
      https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers

     Аргументы:
         request (starlette.requests.Request): экземпляр объекта класса запроса.
             Подробнее: https://www.starlette.io/requests/
         exception (HTTPException): экземпляр объекта пользовательского класса HTTPException.
     Возвращает:
         Экземпляр объекта класса FastAPI.response.JSONResponse, инициализированный с помощью
             kwargs из пользовательского HTTPException.
    """
    print("hello")
    return JSONResponse(
        status_code=exception.status_code,
        content=exception.content,
        headers=exception.headers,
    )
