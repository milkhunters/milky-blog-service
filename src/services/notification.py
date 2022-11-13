import math

from exceptions import APIError
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

    async def get_notifications(self, user_id: int, page_num: int, per_page: int = 10) -> views.NotificationsResponse:
        """
        Получить уведомления

        :param user_id:
        :param page_num: целое положительное число >= 1
        :param per_page: целое положительное число >= 1
        :return:

        # TODO: проверка входных данных, что int32

        """
        if page_num < 1:
            raise APIError(919, "Номер страницы не может быть меньше 1")

        if page_num > 2 ** 31:
            raise APIError(900, "Номер страницы не может быть больше 2**31 (int32)")

        per_page_limit = 40

        # Подготовка входных данных
        per_page = max(min(per_page, per_page_limit, 2147483646), 1)
        limit = min(page_num * per_page, 2147483646)
        skip = min((page_num - 1) * per_page, 2147483646)

        # Подготовка выходных данных
        notifications = await self._repo.search(limit=limit + 1, offset=skip, owner_id=user_id)
        return views.NotificationsResponse(
            items=[views.NotificationResponse.from_orm(notification) for notification in notifications[:per_page]],
            current=page_num,
            next=(page_num + 1) if len(notifications) > per_page else page_num,
            previous=(page_num - 1) if page_num > 1 else page_num
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

    async def delete_notification(self, notification_id: int) -> None:
        """
        Удалить уведомление

        :param notification_id:
        :return:

        TODO:
            1. Возможно нужны проверки на существование уведомления
            2. Возможно стоит обсудить надобность: удалять по мере заполнения
        """
        await self._repo.delete(id=notification_id)

    async def make_read(self, notification_id: int) -> None:
        """
        Сделать уведомление прочитанным

        :param notification_id:
        :return:

        TODO: возможно нужны проверки на существование уведомления
        """
        await self._repo.update(notification_id, is_read=True)
