import uuid
from pydantic import BaseModel

from src.views.base import BaseView


class FileItem(BaseModel):
    id: uuid.UUID
    title: str
    content_type: str


class FileResponse(BaseView):
    message: FileItem
