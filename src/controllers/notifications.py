from fastapi import APIRouter, Depends
from fastapi import Request

from dependencies.jwt_barrier import JWTCookie
from services import NotificationService
import views

from models.schemas import ExceptionsAPIModel


router = APIRouter(
    dependencies=[Depends(JWTCookie())],
    # responses={"4xx": {"model": ExceptionsAPIModel}}
)


@router.get("/get", response_model=views.NotificationsResponse)
async def get_notifications(page: int, request: Request):
    return await NotificationService().get_notifications(request.user.id, page)


@router.post("/read", dependencies=[Depends(JWTCookie())])
async def read_notification(id: int):
    await NotificationService().make_read(id)


@router.delete("/delete")
async def delete_notification(id: int):
    # TODO: подумать над надобностью
    await NotificationService().delete_notification(id)
