from pydantic import BaseModel
from datetime import datetime


class Notification(BaseModel):
    """
    Базовая модель уведомления

    """
    id: int
    type: int
    data: int
    owner_id: int
    is_read: bool
    create_time: datetime

    class Config:
        orm_mode = True
