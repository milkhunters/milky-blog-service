import os
import configparser
from typing import Optional
from dataclasses import dataclass

import consul
from version import __version__

c = consul.Consul()


@dataclass
class RedisConfig:
    host: str
    password: str
    username: Optional[str]
    port: int


@dataclass
class PostgresConfig:
    database: str
    host: str
    port: int
    username: str
    password: str


@dataclass
class S3Config:
    bucket: str
    endpoint_url: str
    region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    service_name: str = "s3"


@dataclass
class DbConfig:
    postgresql: PostgresConfig
    redis: Optional[RedisConfig]
    s3: Optional[S3Config]


@dataclass
class Contact:
    name: str
    url: str
    email: str


@dataclass
class Email:
    isTLS: bool
    isSSL: bool
    host: str
    password: str
    user: str
    port: int


@dataclass
class JWT:
    JWT_ACCESS_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str


@dataclass
class Base:
    name: str
    description: str
    vers: str
    jwt: JWT
    contact: Contact


@dataclass
class Config:
    debug: bool
    mode: str
    build: Optional[int]
    build_date: Optional[str]
    branch: Optional[str]
    commit_hash: Optional[str]
    is_secure_cookie: bool
    base: Base
    email: Email
    db: DbConfig


class KVManager:

    def __init__(self, kv):
        self.config = kv
        self.path_list = ["haha-ton"]  # TODO: сменить на 'milk-back'

    def __getitem__(self, node: str):
        self.path_list.append(node)
        return self

    def value(self):
        path = "/".join(self.path_list)
        value = self.config.get(path)[1]["Value"]
        if value:
            return value.decode("utf-8")
        return None


def load_config() -> Config:
    config = consul.Consul(host="192.168.3.41").kv
    mode = os.getenv('MODE')
    debug = os.getenv('DEBUG')
    build = os.getenv('VERSION_BUILD')
    build_date = os.getenv('VERSION_BUILD_DATE')
    branch = os.getenv('VERSION_BRANCH')
    commit_hash = os.getenv('VERSION_COMMIT_HASH')
    return Config(
        debug=bool(int(debug)),
        mode=mode,
        build=None if not build else int(build),
        build_date=build_date,
        branch=branch,
        commit_hash=commit_hash,
        is_secure_cookie=bool(int(KVManager(config)[mode]["is_secure_cookie"].value())),
        base=Base(
            name=KVManager(config)["base"]["name"].value(),
            description=KVManager(config)["base"]["description"].value(),
            vers=__version__,
            contact=Contact(
                name=KVManager(config)["base"]["contact"]["name"].value(),
                url=KVManager(config)["base"]["contact"]["url"].value(),
                email=KVManager(config)["base"]["contact"]["email"].value()
            ),
            jwt=JWT(
                JWT_ACCESS_SECRET_KEY=KVManager(config)[mode]["jwt"]["JWT_ACCESS_SECRET_KEY"].value(),
                JWT_REFRESH_SECRET_KEY=KVManager(config)[mode]["jwt"]["JWT_REFRESH_SECRET_KEY"].value()
            )
        ),
        db=DbConfig(
            postgresql=PostgresConfig(
                host=KVManager(config)[mode]["database"]["postgresql"]["host"].value(),
                port=int(KVManager(config)[mode]["database"]["postgresql"]["port"].value()),
                username=KVManager(config)[mode]["database"]["postgresql"]["username"].value(),
                password=KVManager(config)[mode]["database"]["postgresql"]["password"].value(),
                database=KVManager(config)[mode]["database"]["postgresql"]["name"].value()
            ),
            redis=RedisConfig(
                host=KVManager(config)[mode]["database"]["redis"]["host"].value(),
                username=None,
                password=KVManager(config)[mode]["database"]["redis"]["password"].value(),
                port=int(KVManager(config)[mode]["database"]["redis"]["port"].value())
            ),
            s3=S3Config(
                endpoint_url=KVManager(config)[mode]["database"]["s3"]["endpoint_url"].value(),
                region_name=KVManager(config)[mode]["database"]["s3"]["region_name"].value(),
                aws_access_key_id=KVManager(config)[mode]["database"]["s3"]["aws_access_key_id"].value(),
                aws_secret_access_key=KVManager(config)[mode]["database"]["s3"]["aws_secret_access_key"].value(),
                bucket=KVManager(config)[mode]["database"]["s3"]["bucket"].value()
            )
        ),
        email=Email(
            isTLS=bool(int(KVManager(config)["base"]["email"]["isTLS"].value())),
            isSSL=bool(int(KVManager(config)["base"]["email"]["isSSL"].value())),
            host=KVManager(config)["base"]["email"]["host"].value(),
            port=int(KVManager(config)["base"]["email"]["port"].value()),
            user=KVManager(config)["base"]["email"]["user"].value(),
            password=KVManager(config)["base"]["email"]["password"].value()
        )
    )


def load_docs(filename: str) -> 'configparser.ConfigParser':
    """
    Загружает документацию из docs файла

    :param filename: *.ini
    :return:
    """
    docs = configparser.ConfigParser()
    docs.read(filenames=f"./docs/{filename}", encoding="utf-8")
    return docs
