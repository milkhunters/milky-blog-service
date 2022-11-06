from fastapi import APIRouter, Depends

from dependencies import JWTCookie, RoleFilter
from models.role import Role
from models.role import MainRole as M
from models.role import AdditionalRole as A


from exceptions.models import ErrorAPIResponse

from . import article
from . import comments

router = APIRouter(responses={"400": {"model": ErrorAPIResponse}})

router.include_router(article.router, prefix="/article")
router.include_router(comments.router, prefix="/comment")
