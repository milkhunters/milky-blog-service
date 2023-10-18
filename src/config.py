import os
from dataclasses import dataclass
from src.version import __version__

import consul


@dataclass
class PostgresConfig:
    DATABASE: str
    USERNAME: str
    PASSWORD: str
    HOST: str
    PORT: int = 5432


@dataclass
class DbConfig:
    POSTGRESQL: PostgresConfig


@dataclass
class Contact:
    NAME: str = None
    URL: str = None
    EMAIL: str = None


@dataclass
class JWT:
    ACCESS_SECRET_KEY: str
    REFRESH_SECRET_KEY: str


@dataclass
class Base:
    TITLE: str
    DESCRIPTION: str
    VERSION: str
    CONTACT: Contact


@dataclass
class Config:
    DEBUG: bool
    JWT: JWT
    BASE: Base
    DB: DbConfig


def to_bool(value) -> bool:
    return str(value).strip().lower() in ("yes", "true", "t", "1")


class KVManager:
    def __init__(self, kv, *, root_name: str):
        self.config = kv
        self.root_name = root_name

    def __call__(self, *args: str) -> int | str | None:
        """
        :param args: list of nodes
        """
        path = "/".join([self.root_name, *args])
        encode_value = self.config.get(path)[1]
        if encode_value and encode_value["Value"]:
            value: str = encode_value['Value'].decode("utf-8")
            if value.isdigit():
                return int(value)
            return value
        return None


def load_consul_config(
        root_name: str,
        *,
        host='127.0.0.1',
        port=8500,
        token=None,
        scheme='http',
        **kwargs
) -> Config:
    """
    Load config from consul

    """

    config = KVManager(
        consul.Consul(
            host=host,
            port=port,
            token=token,
            scheme=scheme,
            **kwargs
        ).kv,
        root_name=root_name
    )
    return Config(
        DEBUG=to_bool(os.getenv('DEBUG', 1)),
        BASE=Base(
            TITLE=config("BASE", "TITLE"),
            DESCRIPTION=config("BASE", "DESCRIPTION"),
            VERSION=__version__,
            CONTACT=Contact(
                NAME=config("BASE", "CONTACT", "NAME"),
                URL=config("BASE", "CONTACT", "URL"),
                EMAIL=config("BASE", "CONTACT", "EMAIL")
            ),
        ),
        JWT=JWT(
            ACCESS_SECRET_KEY=config("JWT", "ACCESS_SECRET_KEY"),
            REFRESH_SECRET_KEY=config("JWT", "REFRESH_SECRET_KEY")
        ),
        DB=DbConfig(
            POSTGRESQL=PostgresConfig(
                HOST=config("DATABASE", "POSTGRESQL", "HOST"),
                PORT=config("DATABASE", "POSTGRESQL", "PORT"),
                USERNAME=config("DATABASE", "POSTGRESQL", "USERNAME"),
                PASSWORD=config("DATABASE", "POSTGRESQL", "PASSWORD"),
                DATABASE=config("DATABASE", "POSTGRESQL", "DATABASE")
            ) if to_bool(config("DATABASE", "POSTGRESQL", "is_used")) else None,
        ),
    )
