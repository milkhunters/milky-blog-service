
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


type FileId = UUID


class File(BaseModel):
    id: FileId
    filename: str
    content_type: str
    is_uploaded: bool

    created_at: datetime
    updated_at: datetime | None
