from pydantic import BaseModel


class Error(BaseModel):
    code: int
    message: str = None


class ExceptionsAPIModel(BaseModel):
    error: Error
