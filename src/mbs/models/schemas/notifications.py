import uuid

from pydantic import BaseModel
from datetime import datetime

from src import NotificationType


class Notification(BaseModel):
    """
    Базовая модель уведомления

    """
    id: uuid.UUID
    type: NotificationType
    content_id: uuid.UUID
    content: str

    created_at: datetime

    class Config:
        from_attributes = True
