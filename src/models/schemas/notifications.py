from typing import Optional

from pydantic import BaseModel
from datetime import datetime

from models.schemas.pagination import PaginationPage


class Notification(BaseModel):
    """
    Одно уведомление

    """
    id: int
    type: int
    data: int
    owner_id: int
    is_read: bool
    create_time: datetime

    class Config:
        orm_mode = True


class Notifications(PaginationPage):
    """
    Несколько уведомлений

    """
    items: Optional[list[Notification]]
