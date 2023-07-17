from src.models.schemas import FileItem
from src.views.base import BaseView


class FileResponse(BaseView):
    content: FileItem
