from pydantic import BaseModel


class Error(BaseModel):
    # TODO: сделать детализированной ошибку
    code: int
    message: str = None


class ErrorAPIResponse(BaseModel):
    error: Error
