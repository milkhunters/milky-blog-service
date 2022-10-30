import math

from models import schemas
import views
from services.repository import NotificationRepo


class NotificationService:

    # TODO: Переписать

    def __init__(
            self,
            notify_repo: NotificationRepo = NotificationRepo()
    ):
        self._repo = notify_repo

    async def get(self, user_id: int, page: int) -> views.NotificationsResponse:
        """
        Получить уведомления

        :param user_id:
        :param page: целое положительное число >=1
        :return:
        """
        per_page = 10

        # Подготовка входных данных
        limit = page * per_page
        skip = (page - 1) * per_page

        # Подготовка выходных данных # TODO: перенести в модель все 3 последние строки
        total_notifications = await self.get_total(user_id)
        total_pages = math.ceil(max(total_notifications, 1) / per_page)
        next_page = (page + 1) if page < total_pages else page
        previous_page = (page - 1) if page > 1 else page
        return views.NotificationsResponse(
            items=await self._repo.get(limit, skip, owner_id=user_id),  # TODO: Модифицировать репозиторий
            current=page,
            total=total_pages,
            next=next_page,
            previous=previous_page
        )

    async def get_total(self, user_id: int) -> int:
        """
        Количество уведомлений пользователя

        :param user_id:
        :return:
        """
        return await self._repo.count(owner_id=user_id)

    async def create(self, user_id: int, notification_type: int, data: int):
        """
        Создать уведомление

        :param user_id:
        :param notification_type: тип из NotificationTypes
        :param data:
        :return:
        """
        return await self._repo.insert(user_id, notification_type, data)  # Todo: реализовать

    async def delete(self, notification_id: int) -> None:
        """
        Удалить уведомление

        :param notification_id:
        :return:

        # TODO: возможно не используемо и следует удалить
        """
        await self._repo.delete(id=notification_id)

    async def make_read(self, notification_id: int) -> None:
        """
        Сделать уведомление прочитанным

        :param notification_id:
        :return:
        """
        await self._repo.update(notification_id, is_read=True)
