from typing import Any, Optional

from pydantic import BaseModel

from src.models.schemas import Error


class BaseView(BaseModel):
    message: Optional[Any]
    error: Optional[Error]
