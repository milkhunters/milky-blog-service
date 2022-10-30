from typing import Optional, Any

from pydantic import BaseModel


class BasePaginationModel(BaseModel):
    items: Optional[list[Any]]
    total_pages: Optional[int]
    next_page: Optional[int]
    current_page: Optional[int]
    previous_page: Optional[int]
