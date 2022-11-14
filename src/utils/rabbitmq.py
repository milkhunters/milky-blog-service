import logging

import aio_pika
import aiormq

from config import load_config

config = load_config()


class RabbitMQ:

    connection = None
    log: logging.Logger = logging.getLogger(__name__)

    @classmethod
    async def open_connection(cls):
        if cls.connection is None:
            cls.log.debug("Инициализация клиента RabbitMQ.")
            cls.connection = await aio_pika.connect_robust(
                host=config.base.amqp.host,
                port=config.base.amqp.port,
                login=config.base.amqp.username,
                password=config.base.amqp.password,
                virtualhost=config.base.amqp.virtualhost
            )
        return cls

    @classmethod
    async def close_connection(cls):
        if cls.connection:
            cls.log.debug("Завершение клиента RabbitMQ.")
            await cls.connection.close()

    @classmethod
    async def send(cls, body: str, routing_key: str, headers: dict = None, content_type: str = None):
        connection = cls.connection

        cls.log.debug(f"Отправка сообщения в очередь {routing_key}.")
        try:

            if connection.is_closed:
                await connection.connect()

            channel = await connection.channel()
            queue = await channel.declare_queue(routing_key, durable=True)

            await channel.default_exchange.publish(
                aio_pika.Message(
                    headers=headers,
                    body=body.encode(),
                    content_type=content_type
                ),
                routing_key=queue.name,
            )
        except aio_pika.exceptions.AMQPException as ex:
            cls.log.exception(
                f"Ошибка при отправке сообщения в очередь {routing_key}: {ex}",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex
