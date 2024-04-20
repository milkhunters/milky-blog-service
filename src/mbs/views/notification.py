from .base import BaseView
from ..models import schemas


class NotificationResponse(BaseView):
    content: schemas.Notification


class NotificationsResponse(BaseView):
    content: list[schemas.Notification]


class NotificationCountResponse(BaseView):
    content: int
