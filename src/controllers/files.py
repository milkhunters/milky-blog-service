from random import randint

from fastapi import APIRouter, File, UploadFile, Depends
from fastapi import Request
from fastapi import Response

from dependencies.auth_bearer import JWTCookie
from dependencies.role_filter import MinRoleFilter
from models.role import Role
from models.role import MainRole as M
from models.role import AdditionalRole as A
from utils.exceptions import APIError
from tortoise.expressions import Q

from models.schemas import ExceptionsAPIModel

router = APIRouter(tags=["Files"], responses={"4xx": {"model": ExceptionsAPIModel}})


@router.post("/files/", dependencies=[Depends(JWTCookie()), Depends(MinRoleFilter(11))])
async def create_file(request: Request, file: bytes = File()):
    # Получить payload
    if request.user.role_id < Role(M.user, A.two):
        raise APIError(401)
    return {"file_size": len(file)}


@router.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}
