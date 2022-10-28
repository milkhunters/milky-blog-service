from fastapi import APIRouter, Depends
from fastapi import Request

from dependencies.auth_bearer import JWTCookie
from services.notification import NotificationService
from utils.exceptions import APIError

from models.schemas import ExceptionsAPIModel
from models import schemas

router = APIRouter(
    tags=["Notifications"],
    prefix="/notifications",
    dependencies=[Depends(JWTCookie())],
    responses={"4xx": {"model": ExceptionsAPIModel}}
)


@router.get("/", response_model=schemas.Notifications)
async def get_notifications(page: int, request: Request):
    page = max(page, 1)
    if page > 2 ** 31:
        raise APIError(900)
    return await NotificationService().get_notifications(request.user.id, page)


@router.post("/read")
async def read_notification(id: int, request: Request):
    ns = NotificationService()
    notification = await ns.get_notification(id)
    if not notification:
        raise APIError(919)
    if notification.owner_id != request.user.id:
        raise APIError(909)
    if not notification.is_read:
        await ns.make_read_notification(id)


@router.delete("/delete")
async def delete_notification(id: int, request: Request):
    ns = NotificationService()
    notification = await ns.get_notification(id)
    if not notification:
        raise APIError(919)
    if notification.owner_id != request.user.id:
        raise APIError(909)
    await ns.delete_notification(id)
