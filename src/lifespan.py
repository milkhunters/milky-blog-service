import asyncio
import logging
import os
from typing import Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from grpc import aio

from src.config import Config
from src.protos.blog_service_control import blog_service_control_pb2_grpc
from src.services.blog_service_control import BlogService

from src.db import create_psql_async_session
from src.services.auth.scheduler import update_reauth_list
from src.utils.s3 import S3Storage


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
    logging.info(f"Starting gRPC server on {listen_addr}")
    await server.start()
    await server.wait_for_termination()


async def init_reauth_checker(app: FastAPI, config: Config):
    scheduler = AsyncIOScheduler()
    ums_grps_host = os.getenv("UMS_GRPC_HOST")
    ums_grps_port = int(os.getenv("UMS_GRPC_PORT"))
    scheduler.add_job(
        update_reauth_list,
        'interval',
        seconds=5,
        args=[app, config, (ums_grps_host, ums_grps_port)]
    )
    logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)
    scheduler.start()


async def init_s3_storage(app: FastAPI, config: Config):
    app.state.file_storage = await S3Storage(
        bucket=config.DB.S3.BUCKET,
        external_host=config.DB.S3.PUBLIC_ENDPOINT_URL
    ).create_session(
        endpoint_url=config.DB.S3.ENDPOINT_URL,
        region_name=config.DB.S3.REGION,
        access_key_id=config.DB.S3.ACCESS_KEY_ID,
        secret_access_key=config.DB.S3.ACCESS_KEY,
    )


def create_start_app_handler(app: FastAPI, config: Config) -> Callable:
    async def start_app() -> None:
        logging.debug("Выполнение FastAPI startup event handler.")
        await init_db(app, config)
        await init_s3_storage(app, config)

        app.state.reauth_session_dict = dict()
        await init_reauth_checker(app, config)

        asyncio.get_running_loop().create_task(grpc_server(app.state))
        logging.info("FastAPI Успешно запущен.")

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        logging.debug("Выполнение FastAPI shutdown event handler.")

    return stop_app
