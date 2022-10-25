from pydantic import BaseModel


class Error(BaseModel):
    code: int
    message: str = None


class ErrorAPIResponse(BaseModel):
    error: Error
