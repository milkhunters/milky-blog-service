import io

from fastapi import APIRouter, Depends
from fastapi import File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.responses import Response
from fastapi.requests import Request

from dependencies import JWTCookie
from services.storage.base import ContentType
from services.storage.s3 import S3
from src.config import load_config

import utils
from views import ErrorAPIResponse

router = APIRouter(responses={"400": {"model": ErrorAPIResponse}})
config = load_config()


@router.get("/{file_id}", response_class=Response)
async def get_file(file_id: str):
    async with S3(
            bucket=config.db.s3.bucket,
            service_name=config.db.s3.service_name,
            endpoint_url=config.db.s3.endpoint_url,
            region_name=config.db.s3.region_name,
            aws_access_key_id=config.db.s3.aws_access_key_id,
            aws_secret_access_key=config.db.s3.aws_secret_access_key,
            path="/user_files"  # TODO: стандартизировать
    ) as s3:
        file = await s3.get(file_id)
        if file:
            return Response(content=file.bytes, media_type=file.content_type.value)
        return {"error": "file not found"}  # todo: выбрасывать исключение


@router.put("/upload_file", dependencies=[Depends(JWTCookie())],)
async def upload_file(file: UploadFile, request: Request):
    try:
        file_type = ContentType(file.content_type)
    except ValueError:
        return {"error": "Unsupported file type"}  # todo: add error handler

    # TODO: Обернуть в логический блок + подумать над проксированием
    chunk_size = 256000

    buffer = b''
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        buffer += chunk

    async with S3(
            bucket=config.db.s3.bucket,
            service_name=config.db.s3.service_name,
            endpoint_url=config.db.s3.endpoint_url,
            region_name=config.db.s3.region_name,
            aws_access_key_id=config.db.s3.aws_access_key_id,
            aws_secret_access_key=config.db.s3.aws_secret_access_key,
            path="/user_files"
    ) as s3:
        return await s3.save(
            name=file.filename.encode("ascii", "ignore").decode(),
            content_type=file_type,
            file=buffer,
            owner_id=request.user.id
        )
