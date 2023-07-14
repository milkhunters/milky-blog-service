from src.models import tables
from src.services.repository.base import BaseRepository


class TagRepo(BaseRepository[tables.Tag]):
    table = tables.Tag
