import uuid

from fastapi import APIRouter, Depends
from fastapi import UploadFile
from fastapi import status as http_status
from fastapi.responses import StreamingResponse

from src.dependencies.services import get_services
from src.services import ServiceFactory
from src.views.file import FileResponse

router = APIRouter()


@router.get("/download/{file_id}", status_code=http_status.HTTP_200_OK)
async def get_file(file_id: uuid.UUID, services: ServiceFactory = Depends(get_services)):
    stream, info = await services.file.get_file(file_id)
    return StreamingResponse(
        stream,
        media_type=info.content_type,
        headers={"Content-Disposition": f"attachment; filename={info.title}"},
    )


@router.post("/upload", response_model=FileResponse, status_code=http_status.HTTP_200_OK)
async def save_file(file: UploadFile, services: ServiceFactory = Depends(get_services)):
    return FileResponse(content=await services.file.upload_file(file))


@router.get("/info/{file_id}", response_model=FileResponse, status_code=http_status.HTTP_200_OK)
async def get_file_info(file_id: uuid.UUID, services: ServiceFactory = Depends(get_services)):
    return FileResponse(content=await services.file.get_file_info(file_id))
