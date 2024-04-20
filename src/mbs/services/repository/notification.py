from mbs.models import tables
from mbs.services.repository.base import BaseRepository


class NotificationRepo(BaseRepository[tables.Notification]):
    table = tables.Notification
