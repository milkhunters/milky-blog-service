from typing import Optional

from models.schemas import BasePaginationModel
from models.schemas import Notification


class NotificationResponse(Notification):
    pass


class NotificationsResponse(BasePaginationModel):
    """
    Список уведомлений

    """
    items: Optional[list[NotificationResponse]]
