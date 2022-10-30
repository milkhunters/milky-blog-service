import random
from contextlib import AsyncExitStack
from typing import Optional, Union, IO

from .base import AbstractStorage, File, ContentType

from aiobotocore.session import AioSession
from config import load_config

config = load_config()


class S3(AbstractStorage):

    def __init__(
            self,
            endpoint_url: str,
            region_name: str,
            aws_access_key_id: str,
            aws_secret_access_key: str,
            bucket: str,
            path: str = "/",
            service_name: str = "s3"
    ):
        self.bucket = bucket
        self.path = path
        self.service_name = service_name
        self.endpoint_url = endpoint_url

        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name

        self._exit_stack = AsyncExitStack()
        self.client = None

    async def __aenter__(self):
        session = AioSession()
        self.client = await self._exit_stack.enter_async_context(
            session.create_client(
                aws_secret_access_key=self.aws_secret_access_key,
                aws_access_key_id=self.aws_access_key_id,
                region_name=self.region_name,

                service_name=self.service_name,
                endpoint_url=self.endpoint_url,
                use_ssl=False
            )
        )
        return self

    async def get(self, file_id: str) -> Optional[File]:
        try:
            response = await self.client.get_object(Bucket=self.bucket, Key=f"{self.path}/{file_id}")
        except Exception:
            # TODO: отловить правильно ошибку: найти botocore.errorfactory.NoSuchKey класс
            return None

        async with response['Body'] as stream:
            return File(
                id=file_id,
                name=response['Metadata']['filename'],
                content_type=ContentType(response['Metadata']['content_type']),
                bytes=await stream.read(),
                owner_id=int(response['Metadata']['owner_id']),
                size=int(response['ContentLength'])
            )

    async def save(self, name: str, content_type: ContentType, file: Union[bytes, IO], owner_id: int) -> str:
        file_id = f"{owner_id}_{random.randint(100000000, 999999999)}"
        await self.client.put_object(
            Bucket=self.bucket,
            Body=file,
            Key=f"{self.path}/{file_id}",
            Metadata={
                "filename": name,
                "owner_id": str(owner_id),
                "content_type": content_type.value
            }
        )
        return file_id

    async def info(self, file_id: str) -> dict:
        response = await self.client.get_object(Bucket=self.bucket, Key=f"{self.path}/{file_id}")
        return {
            "filename": response['Metadata']['filename'],
            "owner_id": response['Metadata']['owner_id'],
            "content_type": ContentType(response['Metadata']['content_type']),
            "size": int(response['ContentLength']),
        }

    async def delete(self, file_id: int) -> None:
        await self.client.delete_object(Bucket=self.bucket, Key=f"{self.path}/{file_id}")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._exit_stack.__aexit__(exc_type, exc_val, exc_tb)
