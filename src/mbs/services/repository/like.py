from mbs.models import tables
from mbs.services.repository.base import BaseRepository


class LikeRepo(BaseRepository[tables.Like]):
    table = tables.Like
