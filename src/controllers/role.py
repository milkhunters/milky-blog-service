import uuid

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src.dependencies.services import get_services
from src.services import ServiceFactory

router = APIRouter()


@router.get("/guest_access", response_model=list[str], status_code=http_status.HTTP_200_OK)
async def role_guest_access(services: ServiceFactory = Depends(get_services)):
    """
    Список доступов для локального гостя

    Требуемые права доступа: None
    """
    return await services.role.guest_access()


@router.get("/app_access", response_model=list[str], status_code=http_status.HTTP_200_OK)
async def role_app_access(services: ServiceFactory = Depends(get_services)):
    """
    Список доступов приложения

    Требуемые права доступа: None
    """
    return await services.role.app_access()
