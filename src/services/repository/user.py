from typing import List, Optional, Union
from tortoise.expressions import Q


from .base import BaseRepo
from src.models import tables


class UserRepo(BaseRepo[tables.User]):
    pass


class DeletedUserRepo(BaseRepo[tables.DeletedUser]):
    pass
