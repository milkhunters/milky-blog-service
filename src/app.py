import logging
import os

import redis.asyncio as redis
import aio_pika

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.models import tables
from src.db import create_sqlite_async_session, create_psql_async_session
from src.middleware.jwt import JWTMiddlewareHTTP
from src.config import load_consul_config
from src.exceptions import APIError, handle_api_error, handle_404_error, handle_pydantic_error

from src.router import register_api_router
from src.utils import RedisClient
from src.utils.fakeredis import FakeRedisPool
from src.utils.openapi import custom_openapi

config = load_consul_config(os.getenv('CONSUL_ROOT', "milk-back-dev"), host="192.168.3.41")
log = logging.getLogger(__name__)

log.debug("Инициализация приложения FastAPI.")
app = FastAPI(
    title=config.BASE.TITLE,
    debug=config.DEBUG,
    version=config.BASE.VERSION,
    description=config.BASE.DESCRIPTION,
    root_path="/api/v1" if not config.DEBUG else "",
    docs_url="/api/docs" if config.DEBUG else "/docs",
    redoc_url="/api/redoc" if config.DEBUG else "/redoc",
    contact={
        "name": config.BASE.CONTACT.NAME,
        "url": config.BASE.CONTACT.URL,
        "email": config.BASE.CONTACT.EMAIL,
    }
)


async def init_db(app: FastAPI):
    if config.DB.POSTGRESQL:
        engine, session = create_psql_async_session(
            host=config.DB.POSTGRESQL.HOST,
            port=config.DB.POSTGRESQL.PORT,
            username=config.DB.POSTGRESQL.USERNAME,
            password=config.DB.POSTGRESQL.PASSWORD,
            database=config.DB.POSTGRESQL.DATABASE,
            echo=config.DEBUG,
        )
    else:
        engine, session = create_sqlite_async_session(
            database='database.db',
            echo=config.DEBUG,
        )
    app.state.db_session = session

    async with engine.begin() as conn:
        # await conn.run_sync(tables.Base.metadata.drop_all)
        await conn.run_sync(tables.Base.metadata.create_all)


async def init_redis_pool(app: FastAPI, db: int = 0):
    if config.DB.REDIS:
        pool = await redis.from_url(
            f"redis://:{config.DB.REDIS.PASSWORD}@{config.DB.REDIS.HOST}:{config.DB.REDIS.PORT}/{db}",
            encoding="utf-8",
            decode_responses=True,
        )
    else:
        pool = FakeRedisPool()
    app.state.redis = RedisClient(pool)


async def init_rabbitmq(app: FastAPI):
    app.state.rmq = await aio_pika.connect_robust(
        host=config.EMAIL.RabbitMQ.HOST,
        port=config.EMAIL.RabbitMQ.PORT,
        login=config.EMAIL.RabbitMQ.USERNAME,
        password=config.EMAIL.RabbitMQ.PASSWORD,
        virtualhost=config.EMAIL.RabbitMQ.VIRTUALHOST,
    )


@app.on_event("startup")
async def on_startup():
    log.debug("Выполнение FastAPI startup event handler.")
    await init_db(app)
    await init_redis_pool(app)
    await init_rabbitmq(app)


@app.on_event("shutdown")
async def on_shutdown():
    log.debug("Выполнение FastAPI shutdown event handler.")
    await app.state.redis.close()
    await app.state.rmq.close()


app.openapi = lambda: custom_openapi(app)
app.state.config = config

log.debug("Добавление маршрутов")
app.include_router(register_api_router(config.DEBUG))
log.debug("Регистрация обработчиков исключений.")
app.add_exception_handler(APIError, handle_api_error)
app.add_exception_handler(404, handle_404_error)
app.add_exception_handler(RequestValidationError, handle_pydantic_error)
log.debug("Регистрация middleware.")
app.add_middleware(JWTMiddlewareHTTP)
