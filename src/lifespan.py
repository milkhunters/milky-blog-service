import asyncio
import logging
from typing import Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from grpc import aio

from src.config import Config
from src.protos.blog_service_control import blog_service_control_pb2_grpc
from src.services.blog_service_control import BlogService

from src.db import create_psql_async_session
from src.services.auth.scheduler import update_reauth_list


async def init_db(app: FastAPI, config: Config):
    engine, session = create_psql_async_session(
        host=config.DB.POSTGRESQL.HOST,
        port=config.DB.POSTGRESQL.PORT,
        username=config.DB.POSTGRESQL.USERNAME,
        password=config.DB.POSTGRESQL.PASSWORD,
        database=config.DB.POSTGRESQL.DATABASE,
        echo=config.DEBUG,
    )
    app.state.db_session = session


async def grpc_server(app_state):
    server = aio.server()
    blog_service_control_pb2_grpc.add_BlogServicer_to_server(BlogService(app_state), server)
    listen_addr = '[::]:50052'
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    await server.wait_for_termination()


async def init_scheduler(app: FastAPI, config: Config):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        update_reauth_list,
        'interval',
        seconds=5,
        args=[app, config],
    )
    scheduler.start()


def create_start_app_handler(app: FastAPI, config: Config) -> Callable:
    async def start_app() -> None:
        logging.debug("Выполнение FastAPI startup event handler.")
        await init_db(app, config)

        app.state.reauth_session_dict = dict()
        await init_scheduler(app, config)

        asyncio.get_running_loop().create_task(grpc_server(app.state))
        logging.info("FastAPI Успешно запущен.")

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        logging.debug("Выполнение FastAPI shutdown event handler.")

    return stop_app
