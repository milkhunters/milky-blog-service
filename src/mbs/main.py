import logging
import os

from fastapi import FastAPI

from mbs.config import load_consul_config


def create_app():

    consul_root = os.getenv('CONSUL_ROOT')
    consul_addr = os.getenv("CONSUL_ADDR")
    service_name = os.getenv("SERVICE_NAME")

    config = load_consul_config(consul_root, addr=consul_addr)
    logging.basicConfig(level=config.log_level)

    app = FastAPI(
        title=config.BASE.TITLE,
        version=config.BASE.VERSION,
        description=config.BASE.DESCRIPTION,
        root_path="/api/blog" if not config.DEBUG else "",
        docs_url="/api/docs" if config.DEBUG else "/docs",
        redoc_url="/api/redoc" if config.DEBUG else "/redoc",
        swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
        contact={
            "name": config.BASE.CONTACT.NAME,
            "url": config.BASE.CONTACT.URL,
            "email": config.BASE.CONTACT.EMAIL,
        },
    )

    app.openapi = lambda: custom_openapi(app, logo_url="https://avatars.githubusercontent.com/u/107867909?s=200&v=4")
    app.state.config = config

    app.add_event_handler("startup", create_start_app_handler(app, config))
    app.add_event_handler("shutdown", create_stop_app_handler(app))

    logging.debug("Добавление маршрутов")
    app.include_router(register_api_router(config.DEBUG))
    logging.debug("Регистрация обработчиков исключений")
    app.add_exception_handler(APIError, handle_api_error)
    app.add_exception_handler(404, handle_404_error)
    app.add_exception_handler(RequestValidationError, handle_pydantic_error)
    logging.debug("Регистрация middleware")
    app.add_middleware(JWTMiddlewareHTTP)
