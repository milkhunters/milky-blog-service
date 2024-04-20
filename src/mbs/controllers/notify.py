import uuid

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src import get_services
from mbs.services import ServiceFactory
from mbs.views import NotificationsResponse, NotificationCountResponse

router = APIRouter()


@router.get("/list", response_model=NotificationsResponse, status_code=http_status.HTTP_200_OK)
async def get_notifications(page: int, per_page: int, services: ServiceFactory = Depends(get_services)):
    """
    Получить список уведомлений пользователя

    Требуемое состояние: ACTIVE

    Требуемые права доступа: GET_SELF_NOTIFICATIONS

    """
    return NotificationsResponse(content=await services.notification.get_notifications(page, per_page))


@router.get("/total", response_model=NotificationCountResponse, status_code=http_status.HTTP_200_OK)
async def get_total(services: ServiceFactory = Depends(get_services)):
    """
    Получить количество уведомлений пользователя

    Требуемое состояние: ACTIVE

    Требуемые права доступа: GET_SELF_NOTIFICATIONS

    """
    return NotificationCountResponse(content=await services.notification.get_total())


@router.delete("/{notification_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def read_notification(notification_id: uuid.UUID, services: ServiceFactory = Depends(get_services)):
    """
    Удалить уведомление пользователя

    Требуемое состояние: ACTIVE

    Требуемые права доступа: DELETE_SELF_NOTIFICATION

    Рекомендуется удалять уведомления, которые пользователь прочитал
    """
    await services.notification.delete_notification(notification_id)
