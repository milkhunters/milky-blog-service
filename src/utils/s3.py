import typing
import uuid
from dataclasses import dataclass
from urllib.parse import urljoin, urlencode

from aiobotocore.session import AioSession
from botocore.exceptions import ClientError


@dataclass
class MetaData:
    filename: str
    content_type: str


class S3Storage:

    def __init__(self, bucket: str, external_host: str, storage_path: str = ""):
        self._bucket = bucket
        self._external_host = external_host
        self._storage_path = storage_path
        self._client = None

    async def create_session(
            self,
            secret_access_key: str,
            access_key_id: str,
            region_name: str,
            endpoint_url: str,
            use_ssl: bool = False
    ):
        session = AioSession()
        self._client = await session.create_client(
            aws_secret_access_key=secret_access_key,
            aws_access_key_id=access_key_id,
            region_name=region_name,
            service_name="s3",
            endpoint_url=endpoint_url,
            use_ssl=use_ssl
        ).__aenter__()
        return self

    async def close(self):
        await self._client.__aexit__()

    async def info(self, file_path: str) -> MetaData | None:
        try:
            response = await self._client.head_object(Bucket=self._bucket, Key=self._storage_path + file_path)
            return MetaData(
                filename=response['ResponseMetadata']['HTTPHeaders'].get('x-amz-meta-filename'),
                content_type=response['ResponseMetadata']['HTTPHeaders'].get('content-type')
            )
        except ClientError:
            return None

    async def generate_upload_url(
            self,
            file_path: str,
            content_type: str,
            content_length: tuple[int, int] = (1048576, 20971520),
            expires_in: int = 3600,
    ):
        # https://stackoverflow.com/a/65234328
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html

        response = await self._client.generate_presigned_post(
            Bucket=self._bucket,
            Key=self._storage_path + file_path,
            Fields={
                "Content-Type": content_type,
            },
            Conditions=[
                ["content-length-range", *content_length],
                {'Content-Type': content_type}
            ],
            ExpiresIn=expires_in
        )
        response['url'] = urljoin(self._external_host, self._bucket)
        return response

    def generate_download_public_url(
            self,
            file_path: str,
            content_type: str,
            rcd: typing.Literal["inline", "attachment"] | str,
            filename: str = None
    ) -> str:
        """
        Получить ссылку на файл
        :param rcd:
        :param content_type:
        :param filename:
        :param file_path:
        :return:

        ---
        rcd: ResponseContentDisposition

        * inline - открывает файл в браузере
        * attachment - скачивает файл

        ---
        """

        base_url = "/".join(item.strip("/") for item in [
            self._external_host,
            self._bucket,
            self._storage_path,
            file_path
        ] if item != "")

        query_params = urlencode({
            "response-content-disposition": rcd + (f"; filename={filename}" if filename else ""),
            "response-content-type": content_type
        })
        return f"{base_url}?{query_params}"

    def delete(self, file_path):
        return self._client.delete_object(Bucket=self._bucket, Key=self._storage_path + file_path)
