from typing import Optional, Any

from pydantic import BaseModel


class PaginationPage(BaseModel):
    items: Optional[Any]
    current_page: Optional[int]
    total_pages: Optional[int]
    next_page: Optional[int]
    previous_page: Optional[int]
