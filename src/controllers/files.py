import io
import uuid

from fastapi import APIRouter, Depends
from fastapi import File, UploadFile
from fastapi import status as http_status
from fastapi.responses import StreamingResponse
from fastapi.responses import Response
from fastapi.requests import Request

from src.dependencies.services import get_services
from src.services import ServiceFactory
from src.views.file import FileResponse

router = APIRouter()


@router.get("/download/{file_id}", status_code=http_status.HTTP_200_OK)
async def get_file(file_id: uuid.UUID, services: ServiceFactory = Depends(get_services)):
    file_bytes = await services.file.get_file(file_id)
    file_info = await services.file.get_file_info(file_id)
    return Response(content=file_bytes, media_type=file_info.content_type)


@router.get("/info/{file_id}", response_model=FileResponse, status_code=http_status.HTTP_200_OK)
async def get_file_info(file_id: uuid.UUID, services: ServiceFactory = Depends(get_services)):
    return FileResponse(message=await services.file.get_file_info(file_id))


@router.post("/save", response_model=FileResponse, status_code=http_status.HTTP_200_OK)
async def save_file(file: UploadFile, services: ServiceFactory = Depends(get_services)):
    return FileResponse(message=await services.file.save_file(file))