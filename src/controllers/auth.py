from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi import status as http_status


from src.views import UserResponse
from src.dependencies.services import get_services
from src.models import schemas
from src.services import ServiceFactory

router = APIRouter()


@router.post("/signUp", response_model=None, status_code=http_status.HTTP_201_CREATED)
async def sign_up(data: schemas.UserCreate, services: ServiceFactory = Depends(get_services)):
    await services.auth.create_user(data)


@router.post("/signIn", response_model=UserResponse, status_code=http_status.HTTP_200_OK)
async def sign_in(user: schemas.UserAuth, response: Response, services: ServiceFactory = Depends(get_services)):
    return UserResponse(content=await services.auth.authenticate(user, response))


@router.post('/logout', response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def logout(request: Request, response: Response, services: ServiceFactory = Depends(get_services)):
    await services.auth.logout(request, response)


@router.post('/refresh_tokens', response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def refresh(request: Request, response: Response, services: ServiceFactory = Depends(get_services)):
    await services.auth.refresh_tokens(request, response)


@router.post("/send/{email}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def send_email(email: str, services: ServiceFactory = Depends(get_services)):
    await services.auth.send_verify_code(email)


@router.post("/confirm/{email}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def confirm_email(email: str, code: int, services: ServiceFactory = Depends(get_services)):
    await services.auth.verify_email(email, code)
