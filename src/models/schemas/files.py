import uuid
from datetime import datetime

from pydantic import BaseModel

from src.models.file_type import FileType


class FileItem(BaseModel):
    id: uuid.UUID
    title: str
    content_type: FileType
    owner_id: uuid.UUID

    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
