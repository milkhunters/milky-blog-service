from src.models import tables
from src.services.repository.base import BaseRepository


class LikeRepo(BaseRepository[tables.Like]):
    table = tables.Like
