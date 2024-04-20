from mbs.models import tables
from mbs.services.repository.base import BaseRepository


class TagRepo(BaseRepository[tables.Tag]):
    table = tables.Tag
