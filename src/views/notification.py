from .base import BaseView
from src.models import schemas


class NotificationResponse(BaseView):
    content: schemas.Notification


class NotificationsResponse(BaseView):
    content: list[schemas.Notification]
