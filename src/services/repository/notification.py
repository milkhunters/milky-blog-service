from models import tables, schemas
from services.repository.base import BaseRepo


class NotificationRepo(BaseRepo[tables.Notification, schemas.Notification]):
    pass

