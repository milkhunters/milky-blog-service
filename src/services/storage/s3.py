import random
import uuid
from contextlib import AsyncExitStack
from typing import Optional, Union, IO, Any

from .base import AbstractStorage, File

from aiobotocore.session import AioSession


class S3Storage(AbstractStorage):

    def __init__(
            self,
            host: str,
            port: int,
            region_name: str,
            access_key: str,
            secret_access_key: str,
            bucket: str,
            service_name: str,
            storage_path="/"
    ):
        self._bucket = bucket
        self._service_name = service_name
        self._endpoint_url = f"http://{host}:{port}"
        self._storage_path = storage_path
        self._access_key = access_key
        self._secret_access_key = secret_access_key
        self._region_name = region_name

        self._exit_stack = AsyncExitStack()
        self._client = None

    async def __aenter__(self):
        session = AioSession()
        self._client = await self._exit_stack.enter_async_context(
            session.create_client(
                aws_secret_access_key=self._secret_access_key,
                aws_access_key_id=self._access_key,
                region_name=self._region_name,

                service_name=self._service_name,
                endpoint_url=self._endpoint_url,
                use_ssl=False
            )
        )
        return self

    async def get(self, file_id: uuid.UUID, load_bytes: bool = False) -> Optional[File]:
        try:
            response = await self._client.get_object(Bucket=self._bucket, Key=self._storage_path + str(file_id))
        except Exception:
            # TODO: отловить правильно ошибку: найти botocore.errorfactory.NoSuchKey исключение
            return None

        file = File(
            id=file_id,
            title=response['Metadata']['filename'],
            content_type=response['Metadata']['content_type'],
            bytes=None,
            owner_id=response['Metadata']['owner_id'],
            size=int(response['ContentLength'])
        )

        if load_bytes:
            async with response['Body'] as stream:
                file.bytes = await stream.read()
        return file

    async def save(self, file_id: uuid.UUID, title: str, content_type: Any, file: Union[bytes, IO], owner_id: uuid.UUID):
        await self._client.put_object(
            Bucket=self._bucket,
            Body=file,
            Key=self._storage_path + str(file_id),
            Metadata={
                "filename": title,
                "owner_id": str(owner_id),
                "content_type": content_type
            }
        )

    async def delete(self, file_id: uuid.UUID) -> None:
        await self._client.delete_object(Bucket=self._bucket, Key=self._storage_path + str(file_id))

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._exit_stack.__aexit__(exc_type, exc_val, exc_tb)