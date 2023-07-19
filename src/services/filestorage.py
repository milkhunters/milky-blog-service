import uuid

import typing
from fastapi import UploadFile
from starlette.responses import AsyncContentStream

from src import exceptions
from src.models import schemas
from src.models.file_type import FileType
from src.models.role import Role, MainRole as M, AdditionalRole as A
from src.models.state import UserState
from src.services.auth import role_filter, state_filter
from src.services.repository import FileRepo
from src.services.storage.s3 import S3Storage


class FileStorageApplicationService:

    def __init__(self, current_user, *, file_repo: FileRepo, file_storage: S3Storage):
        self._current_user = current_user
        self._repo = file_repo
        self._file_storage = file_storage

    async def get_file_info(self, file_id: uuid.UUID) -> schemas.FileItem:
        file = await self._repo.get(id=file_id)
        if not file:
            raise exceptions.NotFound(f"Файл с id:{file_id} не найден")

        return schemas.FileItem.model_validate(file)

    async def get_file(self, file_id: uuid.UUID) -> tuple[typing.AsyncIterable[str | bytes], schemas.FileItem]:
        file = await self._repo.get(id=file_id)
        if not file:
            raise exceptions.NotFound(f"Файл с id:{file_id} не найден")

        return await self._file_storage.get(file_id=file_id), schemas.FileItem.model_validate(file)

    @role_filter(min_role=Role(M.USER, A.ONE))
    @state_filter(UserState.ACTIVE)
    async def upload_file(self, obj: UploadFile) -> schemas.FileItem:
        if not FileType.has_value(obj.content_type):
            raise exceptions.BadRequest(f"Неизвестный тип файла {obj.content_type!r}")

        file = await self._repo.create(
            title=obj.filename,
            content_type=FileType(obj.content_type),
            owner_id=self._current_user.id
        )

        await self._file_storage.save(
            file_id=file.id,
            file=obj.file,
        )

        return schemas.FileItem.model_validate(file)
