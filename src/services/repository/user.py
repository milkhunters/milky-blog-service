from typing import List, Optional, Union
from tortoise.expressions import Q


from .base import BaseRepo
from src.models import tables


class UserRepo(BaseRepo[tables.User]):
    table = tables.User


class DeletedUserRepo(BaseRepo[tables.DeletedUser]):
    table = tables.DeletedUser
