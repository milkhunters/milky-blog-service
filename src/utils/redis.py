"""Redis client class utility."""
import logging

import aioredis
import aioredis.sentinel
from aioredis.exceptions import RedisError
from config import load_config

config = load_config()


class RedisClient(object):
    """Определение утилиты Redis.
     Служебный класс для обработки подключения к базе данных Redis и операций.
    Attributes:
        redis_client (aioredis.Redis, optional): Экземпляр клиентского объекта Redis.
        log (logging.Logger): Обработчик ведения журнала для этого класса.
        base_redis_init_kwargs (dict): Общие kwargs независимо от других Redis
            конфигурациях.
        connection_kwargs (dict, optional): Дополнительные kwargs для инициализации
            объекта Redis.
    """

    redis_client: aioredis.Redis = None
    log: logging.Logger = logging.getLogger(__name__)
    base_redis_init_kwargs: dict = {
        "encoding": "utf-8",
        "decode_responses": True,
        "port": config.db.redis.port,
    }
    connection_kwargs: dict = {}

    @classmethod
    def open_redis_client(cls):
        """Создает экземпляр объекта сеанса клиента Redis.
         В зависимости от конфигурации создает клиент Redis или Redis Sentinel.
        Returns:
            aioredis.Redis: Экземпляр объекта Redis.
        """
        if cls.redis_client is None:
            cls.log.debug("Инициализация клиента Redis.")

            if config.db.redis.username:
                cls.connection_kwargs.update({"username": config.db.redis.username})
            if config.db.redis.password:
                cls.connection_kwargs.update({"password": config.db.redis.password})

            # if redis_conf.REDIS_USE_SENTINEL:
            #     sentinel = aioredis.sentinel.Sentinel(
            #         [(redis_conf.REDIS_HOST, redis_conf.REDIS_PORT)],
            #         sentinel_kwargs=cls.connection_kwargs,
            #     )
            #     cls.redis_client = sentinel.master_for("mymaster")
            # else:

            cls.base_redis_init_kwargs.update(cls.connection_kwargs)
            cls.redis_client = aioredis.from_url(
                "redis://{0:s}/0".format(config.db.redis.host),
                **cls.base_redis_init_kwargs,
            )
        return cls.redis_client

    @classmethod
    async def close_redis_client(cls):
        """Завершение клиента Redis."""
        if cls.redis_client:
            cls.log.debug("Завершение клиента Redis.")
            await cls.redis_client.close()

    @classmethod
    async def ping(cls):
        """Выполнить команду Redis PING.
         Пингует сервер Redis.
        Returns:
            response: Логическое значение, может ли клиент Redis пинговать сервер Redis.
        Raises:
            aioredis.RedisError: Если клиент Redis дал сбой при выполнении команды.
        """
        redis_client = cls.redis_client

        cls.log.debug("Сформирована Redis PING команда")
        try:
            return await redis_client.ping()
        except RedisError as ex:
            cls.log.exception(
                "Команда Redis PING завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            return False

    @classmethod
    async def set(cls, key: str, value: str, expire: int = 2592000):
        """Выполнить команду Redis SET.
         Установите ключ для хранения строкового значения. Если ключ уже содержит значение, оно
         перезаписывается независимо от его типа.
        Args:
            key (str): Ключ.
            value (str): Значение, которое необходимо установить.
            expire (int): Время в секундах, по истечении которого ключ будет удален.
            (по умолчанию 30 дней)
        Returns:
            response: Ответ команды Redis SET, для получения дополнительной информации
                look: https://redis.io/commands/set#return-value
        Raises:
            aioredis.RedisError: Если клиент Redis дал сбой при выполнении команды.
        """
        redis_client = cls.redis_client

        cls.log.debug(f"Сформирована Redis SET команда, key: {key}, value: {value}")
        try:
            await redis_client.set(key, value)
            await redis_client.expire(key, expire)
        except RedisError as ex:
            cls.log.exception(
                "Команда Redis SET завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    @classmethod
    async def rpush(cls, key, value):
        """Выполнить команду Redis RPUSH.
         Вставляет все указанные значения в конец списка, хранящегося в ключе.
         Если ключ не существует, он создается как пустой список перед выполнением
         операция проталкивания. Когда ключ содержит значение, не являющееся списком,
         возвращается ошибка.
        Args:
            key (str): Ключ.
            value (str, list): Одно или несколько значений для добавления.
        Returns:
            response: Длина списка после операции push.
        Raises:
            aioredis.RedisError: Если клиент Redis дал сбой при выполнении команды.
        """
        redis_client = cls.redis_client

        cls.log.debug(f"Сформирована Redis RPUSH команда, key: {key}, value: {value}")
        try:
            await redis_client.rpush(key, value)
        except RedisError as ex:
            cls.log.exception(
                "Команда Redis RPUSH завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    @classmethod
    async def exists(cls, key):
        """Выполнить команду Redis EXISTS.
        Возвращает True, если ключ существует.
        Args:
            key (str): Redis db key.
        Returns:
            response: Логическое значение, определяющее, существует ли ключ в Redis db.
        Raises:
            aioredis.RedisError: Если клиент Redis дал сбой при выполнении команды.
        """
        redis_client = cls.redis_client

        cls.log.debug(f"Сформирована Redis EXISTS команда, key: {key}, exists")
        try:
            return await redis_client.exists(key)
        except RedisError as ex:
            cls.log.exception(
                "Команда Redis EXISTS завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    @classmethod
    async def get(cls, key):
        """Выполнить команду Redis GET.
         Получает значение ключа. Если ключ не существует, то возвращается специальное
         значение None. Возвращается исключение, если значение, хранящееся в ключе, не является
         string, потому что GET обрабатывает только строковые значения.
        Args:
            key (str): Ключ.
        Returns:
            response: Значение ключа.
        Raises:
            aioredis.RedisError: Если клиент Redis дал сбой при выполнении команды.
        """
        redis_client = cls.redis_client

        cls.log.debug(f"Сформирована Redis GET команда, key: {key}")
        try:
            return await redis_client.get(key)
        except RedisError as ex:
            cls.log.exception(
                "Команда Redis GET завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    @classmethod
    async def lrange(cls, key, start, end):
        """Выполнить команду Redis LRANGE.
         Возвращает указанные элементы списка, хранящегося в ключе. Смещения
         start и stop — это индексы, начинающиеся с нуля, где 0 — первый элемент
         списка (голова списка), 1 — следующий элемент и так далее.
         Эти смещения также могут быть отрицательными числами, указывающими, что смещения начинаются
         в конце списка. Например, -1 — это последний элемент
         список, -2 предпоследний и так далее.
        Args:
            key (str): Ключ.
            start (int): Начальное значение смещения.
            end (int): Конечное значение смещения.
        Returns:
            response: Возвращает указанные элементы списка, хранящегося в ключе.
        Raises:
            aioredis.RedisError: Если клиент Redis дал сбой при выполнении команды.
        """
        redis_client = cls.redis_client

        cls.log.debug(f"Сформирована Redis LRANGE команда, key: {key}, start: {start}, end: {end}")
        try:
            return await redis_client.lrange(key, start, end)
        except RedisError as ex:
            cls.log.exception(
                "Команда Redis LRANGE завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    @classmethod
    async def delete(cls, key: str):
        redis_client = cls.redis_client

        cls.log.debug(f"Сформирована Redis DELETE команда, key: {key}")
        try:
            return await redis_client.delete(key)
        except RedisError as ex:
            cls.log.exception(
                "Команда Redis DELETE завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex
