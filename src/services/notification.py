import math

from database.notification import NotificationManager
from models import schemas


class NotificationService:

    # Переписать

    def __init__(self):
        self._db = NotificationManager()
        # Установки
        self.per_page = 10

    async def get_notifications(self, user_id: int, page: int) -> schemas.Notifications:
        """
        Получить уведомления

        :param user_id:
        :param page: целое положительное число >=1
        :return:
        """
        # Подготовка входных данных
        limit = page * self.per_page
        skip = (page - 1) * self.per_page
        # Выполнение
        raw_notifications = await self._db.get_notifications(limit, skip, owner_id=user_id)
        # Подготовка выходных данных
        total_notifications = await self.get_total_notifications(user_id)
        total_pages = math.ceil(max(total_notifications, 1)/self.per_page)
        next_page = (page + 1) if page < total_pages else page
        previous_page = (page - 1) if page > 1 else page
        return schemas.Notifications(
            items=[schemas.Notification.from_orm(notification) for notification in raw_notifications],
            current_page=page,
            total_pages=total_pages,
            next_page=next_page,
            previous_page=previous_page
        )

    async def get_notification(self, notification_id: int):
        """
        Получить информацию об уведомлении

        :param notification_id:
        :return:
        """
        notification = await self._db.get_notification(notification_id)
        return notification

    async def get_total_notifications(self, user_id: int) -> int:
        """
        Количество уведомлений пользователя

        :param user_id:
        :return:
        """
        return await self._db.get_count_of_notifications(user_id)

    async def create_notification(self, user_id: int, notification_type: int, data: int):
        """
        Создать уведомление

        :param user_id:
        :param notification_type: тип из NotificationTypes
        :param data:
        :return:
        """
        return await self._db.create_notification(user_id, notification_type, data)

    async def delete_notification(self, notification_id: int) -> None:
        """
        Удалить уведомление

        :param notification_id:
        :return:
        """
        await self._db.delete_notification(notification_id)

    async def make_read_notification(self, notification_id: int) -> None:
        """
        Сделать уведомление прочитанным

        :param notification_id:
        :return:
        """
        await self._db.update_notification(notification_id, is_read=True)
