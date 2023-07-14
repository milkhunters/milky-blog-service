from src.models import tables
from src.services.repository.base import BaseRepository


class NotificationRepo(BaseRepository[tables.Notification]):
    table = tables.Notification
