import uuid

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src.dependencies.services import get_services
from src.services import ServiceFactory
from src.views import NotificationsResponse, NotificationCountResponse

router = APIRouter()


@router.get("/list", response_model=NotificationsResponse, status_code=http_status.HTTP_200_OK)
async def get_notifications(page: int, per_page: int, services: ServiceFactory = Depends(get_services)):
    """
    Получить список уведомлений пользователя

    Минимальная роль: USER.ONE

    Состояние: ACTIVE

    """
    return NotificationsResponse(content=await services.notification.get_notifications(page, per_page))


@router.get("/total", response_model=NotificationCountResponse, status_code=http_status.HTTP_200_OK)
async def get_total(services: ServiceFactory = Depends(get_services)):
    """
    Получить количество уведомлений пользователя

    Минимальная роль: USER.ONE

    Состояние: ACTIVE
    """
    return NotificationCountResponse(content=await services.notification.get_total())


@router.delete("/delete/{notification_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def read_notification(notification_id: uuid.UUID, services: ServiceFactory = Depends(get_services)):
    """
    Удалить уведомление пользователя

    Минимальная роль: USER.ONE

    Состояние: ACTIVE

    Рекомендуется удалять уведомления, которые пользователь прочитал
    """
    await services.notification.delete_notification(notification_id)
