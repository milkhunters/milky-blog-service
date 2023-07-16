from fastapi import APIRouter

from . import article
from . import comments

router = APIRouter()

router.include_router(article.router, prefix="/article")
router.include_router(comments.router, prefix="/comment")
