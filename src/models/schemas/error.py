from typing import Any

from src.models.error import ErrorType
from pydantic import BaseModel


class Error(BaseModel):
    type: ErrorType
    content: Any


class FieldErrorItem(BaseModel):
    field: str
    location: list[str]
    message: str
    type: str
