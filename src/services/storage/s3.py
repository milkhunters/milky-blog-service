import uuid
from typing import IO, Any
from aiobotocore.response import StreamingBody

from .base import AbstractStorage

from aiobotocore.session import AioSession


class S3Storage(AbstractStorage):

    def __init__(self, bucket: str, storage_path="/"):
        self._bucket = bucket
        self._storage_path = storage_path
        self._client = None

    async def create_session(
            self,
            secret_access_key: str,
            access_key_id: str,
            region_name: str,
            service_name: str,
            endpoint_url: str,
            use_ssl: bool = False
    ):
        session = AioSession()
        self._client = await session.create_client(
            aws_secret_access_key=secret_access_key,
            aws_access_key_id=access_key_id,
            region_name=region_name,
            service_name=service_name,
            endpoint_url=endpoint_url,
            use_ssl=use_ssl
        ).__aenter__()
        return self

    async def close(self):
        await self._client.__aexit__()

    async def get(self, file_id: uuid.UUID) -> StreamingBody:
        response = await self._client.get_object(Bucket=self._bucket, Key=self._storage_path + str(file_id))
        return response['Body']

    async def save(self, file_id: uuid.UUID, file: bytes | IO):
        await self._client.put_object(
            Bucket=self._bucket,
            Body=file,
            Key=self._storage_path + str(file_id),
        )

    async def delete(self, file_id: uuid.UUID) -> None:
        await self._client.delete_object(Bucket=self._bucket, Key=self._storage_path + str(file_id))
