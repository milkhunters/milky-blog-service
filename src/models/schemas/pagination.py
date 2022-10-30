from typing import Optional, Any

from pydantic import BaseModel


class BasePaginationModel(BaseModel):
    items: Optional[list[Any]]
    total: Optional[int]
    next: Optional[int]
    current: Optional[int]
    previous: Optional[int]
