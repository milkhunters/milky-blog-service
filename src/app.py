"""Application implementation - ASGI."""
import logging
import urllib.parse

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from tortoise.contrib.fastapi import register_tortoise

from middleware import JWTMiddleware
from src.config import load_config
from src.exceptions.api import APIError
from src.exceptions.api import not_found_exception_handler
from src.exceptions.api import validation_exception_handler
from src.exceptions.api import api_exception_handler

from src.router import root_api_router
from src.utils import RedisClient, AiohttpClient

config = load_config()
log = logging.getLogger(__name__)

log.debug("Инициализация приложения FastAPI.")
app = FastAPI(
    title=config.base.name,
    debug=config.debug,
    version=config.base.vers,
    description=config.base.description,
    root_path="/api" if not config.debug else "/",
    docs_url="/api/docs" if config.debug else "/docs",
    redoc_url="/api/redoc" if config.debug else "/redoc",
    contact={
        "name": config.base.contact.name,
        "url": config.base.contact.url,
        "email": config.base.contact.email,
    }
)

register_tortoise(
    app,
    db_url="postgres://{user}:{password}@{host}:{port}/{database}".format(
        user=config.db.postgresql.username,
        password=urllib.parse.quote_plus(config.db.postgresql.password),
        host=config.db.postgresql.host,
        port=config.db.postgresql.port,
        database=config.db.postgresql.database
    ),
    modules={"models": ["src.models.tables"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.on_event("startup")
async def on_startup():
    log.debug("Выполнение обработчика события старта FastAPI.")
    if config.db.redis:
        await RedisClient.open_redis_client()
    AiohttpClient.get_aiohttp_client()


@app.on_event("shutdown")
async def on_shutdown():
    log.debug("Выполнение обработчика события закрытия FastAPI.")
    # Gracefully close utilities.
    if config.db.redis:
        await RedisClient.close_redis_client()
    await AiohttpClient.close_aiohttp_client()


log.debug("Добавление маршрутов приложения.")
app.include_router(root_api_router)
log.debug("Регистрация обработчиков исключений.")
app.add_exception_handler(APIError, api_exception_handler)
app.add_exception_handler(404, not_found_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
log.debug("Регистрация промежуточного ПО.")
app.add_middleware(JWTMiddleware)
