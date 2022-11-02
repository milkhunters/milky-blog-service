from typing import List, Optional, Union
from tortoise.expressions import Q

from models import schemas
from .base import BaseRepo
from src.models import tables


class UserRepo(BaseRepo[tables.User, schemas.User]):
    pass


class DeletedUserRepo(BaseRepo[tables.DeletedUser, schemas.DeletedUser]):
    pass
