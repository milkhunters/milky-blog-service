from dataclasses import dataclass

import consul
import urllib.parse


@dataclass
class PostgresConfig:
    DATABASE: str
    USERNAME: str
    PASSWORD: str
    HOST: str
    PORT: int


@dataclass
class S3Config:
    BUCKET: str
    ENDPOINT_URL: str
    PUBLIC_ENDPOINT_URL: str
    REGION: str
    ACCESS_KEY_ID: str
    ACCESS_KEY: str


@dataclass
class DbConfig:
    POSTGRESQL: PostgresConfig
    S3: S3Config


@dataclass
class Contact:
    NAME: str = None
    URL: str = None
    EMAIL: str = None


@dataclass
class Base:
    TITLE: str
    DESCRIPTION: str
    VERSION: str
    CONTACT: Contact


@dataclass
class Config:
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
        addr: str = "http://localhost:8500",
        token: str = None,
        **kwargs
) -> Config:
    """
    Load config from consul

    """
    url = urllib.parse.urlparse(addr)
    config = KVManager(
        consul.Consul(
            host=url.hostname,
            port=url.port,
            token=token,
            scheme=url.scheme,
            **kwargs
        ).kv,
        root_name=root_name
    )
    return Config(
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
        DB=DbConfig(
            POSTGRESQL=PostgresConfig(
                HOST=config("DATABASE", "POSTGRESQL", "HOST"),
                PORT=config("DATABASE", "POSTGRESQL", "PORT"),
                USERNAME=config("DATABASE", "POSTGRESQL", "USERNAME"),
                PASSWORD=config("DATABASE", "POSTGRESQL", "PASSWORD"),
                DATABASE=config("DATABASE", "POSTGRESQL", "DATABASE")
            ),
            S3=S3Config(
                ENDPOINT_URL=config("DATABASE", "S3", "ENDPOINT_URL"),
                REGION=config("DATABASE", "S3", "REGION"),
                ACCESS_KEY_ID=config("DATABASE", "S3", "ACCESS_KEY_ID"),
                ACCESS_KEY=config("DATABASE", "S3", "ACCESS_KEY"),
                BUCKET=config("DATABASE", "S3", "BUCKET"),
                PUBLIC_ENDPOINT_URL=config("DATABASE", "S3", "PUBLIC_ENDPOINT_URL")
            ),
        ),
    )
