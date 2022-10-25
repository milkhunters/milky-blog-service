import json
import typing
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from views import ErrorAPIResponse, Error

with open("error_list.json", "r", encoding="utf-8") as file:
    error_list = json.load(file)


def get_error_data(error_code: int) -> dict:
    code_str = str(error_code)
    default_error_data = {
        "http_status_code": 400,
        "message": "Неопознанная ошибка API"
    }
    return error_list.get(code_str, default_error_data)


class APIError(StarletteHTTPException):
    def __init__(
            self,
            api_code: int,
            headers: typing.Optional[dict] = None
    ) -> None:
        self.api_code = api_code
        super().__init__(status_code=400, headers=headers)


async def validation_exception_handler(request, exc):
    data = get_error_data(900)
    return JSONResponse(
        status_code=data["http_status_code"],
        content=ErrorAPIResponse(
            error=Error(
                code=900,
                message=data["message"]
            )
        ).dict()
    )


async def not_found_exception_handler(request, exc):
    data = get_error_data(919)
    return JSONResponse(
        status_code=data["http_status_code"],
        content=ErrorAPIResponse(
            error=Error(
                code=919,
                message=data["message"]
            )
        ).dict()
    )


async def api_exception_handler(request, exc):
    data = get_error_data(exc.api_code)
    return JSONResponse(
        status_code=data["http_status_code"],
        content=ErrorAPIResponse(
            error=Error(
                code=exc.api_code,
                message=data["message"]
            )
        ).dict()
    )
