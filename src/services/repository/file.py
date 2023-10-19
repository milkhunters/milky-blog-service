from src.models import tables
from src.services.repository.base import BaseRepository


class FileRepo(BaseRepository[tables.File]):
    table = tables.File
