import uuid
import datetime

from mbs.domain.models import File


class FileService:

    def create_file(
            self,
            filename: str,
            content_type: str,
    ):
        return File(
            id=uuid.uuid4(),
            filename=filename,
            content_type=content_type,
            is_uploaded=False,
            created_at=datetime.datetime.now(datetime.UTC),
            updated_at=None
        )

    def make_uploaded(self, file: File):
        return File(
            id=file.id,
            filename=file.filename,
            content_type=file.content_type,
            is_uploaded=True,
            created_at=file.created_at,
            updated_at=datetime.datetime.now(datetime.UTC)
        )