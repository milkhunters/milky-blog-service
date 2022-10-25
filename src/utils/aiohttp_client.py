"""Aiohttp client class utility."""
import logging
import asyncio
from typing import Optional
from socket import AF_INET

import aiohttp


SIZE_POOL_AIOHTTP = 100


class AiohttpClient(object):
    """Утилита клиента сеанса Aiohttp.
    Служебный класс для обработки асинхронного HTTP-запроса для всей области
    приложения FastAPI.
    Атрибуты:
         sem (asyncio.Semaphore, необязательно): значение семафора.
         aiohttp_client (aiohttp.ClientSession, необязательно): сеанс клиента Aiohttp.
             экземпляр объекта.
    """

    sem: Optional[asyncio.Semaphore] = None
    aiohttp_client: Optional[aiohttp.ClientSession] = None
    log: logging.Logger = logging.getLogger(__name__)

    @classmethod
    def get_aiohttp_client(cls):
        """Создает экземпляр объекта сеанса клиента aiohttp.
         :return:
             aiohttp.ClientSession: экземпляр объекта ClientSession.
        """
        if cls.aiohttp_client is None:
            cls.log.debug("Initialize AiohttpClient session.")
            timeout = aiohttp.ClientTimeout(total=2)
            connector = aiohttp.TCPConnector(
                family=AF_INET,
                limit_per_host=SIZE_POOL_AIOHTTP,
            )
            cls.aiohttp_client = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
            )

        return cls.aiohttp_client

    @classmethod
    async def close_aiohttp_client(cls):
        """Закрывает сеанс клиента aiohttp."""
        if cls.aiohttp_client:
            cls.log.debug("Close AiohttpClient session.")
            await cls.aiohttp_client.close()
            cls.aiohttp_client = None

    @classmethod
    async def get(cls, url, headers=None, raise_for_status=False):
        """Выполнить запрос HTTP GET.
         Аргументы:
             url (str): конечная точка запроса HTTP GET.
             заголовки (dict): необязательные заголовки HTTP для отправки с запросом.
             raise_for_status (bool): автоматически вызывать
                 ClientResponse.raise_for_status() для ответа, если установлено значение True.
         Возвращает:
             response: ответ на запрос HTTP GET — aiohttp.ClientResponse
                 экземпляр объекта.
        """
        client = cls.get_aiohttp_client()

        cls.log.debug("Started GET {}".format(url))
        response = await client.get(
            url,
            headers=headers,
            raise_for_status=raise_for_status,
        )

        return response

    @classmethod
    async def post(cls, url, data=None, headers=None, raise_for_status=False):
        """Выполнение HTTP POST-запроса.
         Аргументы:
             url (str): конечная точка запроса HTTP POST.
             data (любые): данные для отправки в теле запроса. Это может
                 быть объектом FormData или чем-либо, что может быть передано в
                 Данные формы, например. словарь, байты или файловый объект.
             заголовки (dict): необязательные заголовки HTTP для отправки с запросом.
             raise_for_status (bool): автоматически вызывать
                 ClientResponse.raise_for_status() для ответа, если установлено значение True.
         Возвращает:
             ответ: ответ на HTTP-запрос POST — aiohttp.ClientResponse
                 экземпляр объекта.
        """
        client = cls.get_aiohttp_client()

        cls.log.debug("Started POST {}".format(url))
        response = await client.post(
            url,
            data=data,
            headers=headers,
            raise_for_status=raise_for_status,
        )

        return response

    @classmethod
    async def put(cls, url, data=None, headers=None, raise_for_status=False):
        """Выполнить HTTP-запрос PUT.
         Аргументы:
             url (str): конечная точка запроса HTTP PUT.
             data (любые): данные для отправки в теле запроса. Это может
                 быть объектом FormData или чем-либо, что может быть передано в
                 Данные формы, например. словарь, байты или файловый объект.
             заголовки (dict): необязательные заголовки HTTP для отправки с запросом.
             raise_for_status (bool): автоматически вызывать
                 ClientResponse.raise_for_status() для ответа, если установлено значение True.
         Возвращает:
             ответ: ответ на HTTP-запрос PUT — aiohttp.ClientResponse
                 экземпляр объекта.
        """
        client = cls.get_aiohttp_client()

        cls.log.debug("Started PUT {}".format(url))
        response = await client.put(
            url,
            data=data,
            headers=headers,
            raise_for_status=raise_for_status,
        )

        return response

    @classmethod
    async def delete(cls, url, headers=None, raise_for_status=False):
        """Выполнить запрос HTTP DELETE.
         Аргументы:
             url (str): конечная точка HTTP-запроса DELETE.
             заголовки (dict): необязательные заголовки HTTP для отправки с запросом.
             raise_for_status (bool): автоматически вызывать
                 ClientResponse.raise_for_status() для ответа, если установлено значение True.
         Возвращает:
             ответ: ответ на запрос HTTP DELETE — aiohttp.ClientResponse
                 экземпляр объекта.
        """
        client = cls.get_aiohttp_client()

        cls.log.debug("Started DELETE {}".format(url))
        response = await client.delete(
            url,
            headers=headers,
            raise_for_status=raise_for_status,
        )

        return response

    @classmethod
    async def patch(cls, url, data=None, headers=None, raise_for_status=False):
        """Выполнить запрос HTTP PATCH.
         Аргументы:
             url (str): конечная точка запроса HTTP PATCH.
             data (любые): данные для отправки в теле запроса. Это может
                 быть объектом FormData или чем-либо, что может быть передано в
                 Данные формы, например. словарь, байты или файловый объект.
             заголовки (dict): необязательные заголовки HTTP для отправки с запросом.
             raise_for_status (bool): автоматически вызывать
                 ClientResponse.raise_for_status() для ответа, если установлено значение True.
         Возвращает:
             ответ: ответ на запрос HTTP PATCH — aiohttp.ClientResponse
                 экземпляр объекта.
        """
        client = cls.get_aiohttp_client()

        cls.log.debug("Started PATCH {}".format(url))
        response = await client.patch(
            url,
            data=data,
            headers=headers,
            raise_for_status=raise_for_status,
        )

        return response
