# import uuid
#
# from fastapi import UploadFile
#
# from src import exceptions
# from src.models import schemas
# from src.models.role import Role, MainRole as M, AdditionalRole as A
# from src.services.auth import role_filter
# from src.services.repository import FileRepo
# from src.services.storage.base import AbstractStorage, File
#
#
# class FileStorageApplicationService:
#
#     def __init__(self, current_user, *, file_repo: FileRepo, file_storage: AbstractStorage):
#         self._current_user = current_user
#         self._repo = file_repo
#         self._file_storage = file_storage
#
#     @role_filter(min_role=Role(M.USER, A.ONE))
#     async def get_file_info(self, file_id: uuid.UUID) -> views.FileItem:
#         file = await self._repo.get(id=file_id)
#         if not file:
#             raise exceptions.NotFound(f"Файл с id:{file_id} не найден")
#
#         async with self._file_storage as storage:
#             file_info = await storage.get(
#                 file_id=file_id,
#                 load_bytes=False
#             )
#
#         if not file_info:
#             raise exceptions.NotFound(f"Файл с id:{file_id} удален с хранилища")
#
#         return FileItem(
#             id=file_id,
#             title="noname" if not file.file_name else file.file_name,
#             content_type=file_info.content_type
#         )
#
#     @role_filter(roles=[UserRole.ADMIN, UserRole.HIGH_USER, UserRole.USER])
#     async def get_file(self, file_id: uuid.UUID):
#         file = await self._file_repo.get(id=file_id)
#         if not file:
#             raise NotFound(f"Файл с id {file_id!r} не найден")
#
#         async with self._file_storage as storage:
#             file_info = await storage.get(
#                 file_id=file_id,
#                 load_bytes=True
#             )
#
#         if not file_info:
#             raise NotFound(f"Файл с id {file_id!r} удален с хранилища")
#
#         return file_info.bytes
#
#     @role_filter(roles=[UserRole.ADMIN, UserRole.HIGH_USER, UserRole.USER])
#     async def save_file(self, file: UploadFile) -> views.FileItem:
#         if not ContentType.has_value(file.content_type):
#             raise BadRequest(f"Неизвестный тип файла {file.content_type!r}")
#
#         # if len(file) > 20971520:
#         #     pass
#
#         # todo: filename null case
#
#         file_id = await self._file_repo.create(
#             file_name=file.filename
#         )
#
#         async with self._file_storage as storage:
#             await storage.save(
#                 file_id=file_id,
#                 title=file.filename,
#                 content_type=file.content_type,
#                 file=await file.read(),
#                 owner_id=self._current_user.id
#             )
#         return views.FileItem(
#             id=file_id,
#             title="noname" if not file.filename else file.filename,
#             content_type=file.content_type
#         )
