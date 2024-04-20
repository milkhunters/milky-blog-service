from mbs.models import tables
from mbs.services.repository.base import BaseRepository


class FileRepo(BaseRepository[tables.File]):
    table = tables.File
