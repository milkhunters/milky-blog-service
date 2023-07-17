from fastapi import APIRouter

from src.controllers import super
from src.controllers import auth
from src.controllers import user
from src.controllers import stats
from src.controllers import blog
from src.controllers import notify
from src.controllers import files


def register_api_router(is_debug: bool) -> APIRouter:
    root_api_router = APIRouter(prefix="/api/v1" if is_debug else "")

    root_api_router.include_router(super.router, prefix="/super", tags=["Admin"])
    root_api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
    root_api_router.include_router(user.router, prefix="/user", tags=["User"])
    root_api_router.include_router(notify.router, prefix="/notification", tags=["Notification"])
    root_api_router.include_router(blog.router, prefix="/blog", tags=["Blog"])
    root_api_router.include_router(stats.router, prefix="", tags=["Stats"])
    root_api_router.include_router(files.router, prefix="/file", tags=["File"])

    return root_api_router
