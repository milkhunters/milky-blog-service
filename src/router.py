from fastapi import APIRouter

from controllers import admin
from controllers import auth
from controllers import user
from controllers import stats
from controllers import email
from controllers import blog
from controllers import notifications

from config import load_config

config = load_config()

root_api_router = APIRouter(prefix="/api/v1" if config.debug else "",)

root_api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
root_api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
root_api_router.include_router(email.router, prefix="/email", tags=["Email"])
root_api_router.include_router(user.router, prefix="/user", tags=["User"])
root_api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
root_api_router.include_router(blog.router, prefix="/blog", tags=["Blog"])
root_api_router.include_router(stats.router, prefix="", tags=["Stats"])
