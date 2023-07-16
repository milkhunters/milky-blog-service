import aio_pika

from src.config import Email


class EmailService:
    def __init__(self, rmq: aio_pika.RobustConnection, config: Email):
        self._rmq = rmq
        self._config = config

    async def send_mail(self, email: str, subject: str, message: str, content_type: str = "text/html"):
        """
        Отправляет сообщение на почту

        :param email: почта получателя.
        :param subject: тема сообщения
        :param message: текст сообщения
        :param content_type: тип контента
        """

        channel = await self._rmq.channel()
        queue = await channel.declare_queue(self._config.RabbitMQ.QUEUE, durable=True)

        await channel.default_exchange.publish(
            aio_pika.Message(
                headers={
                    "To": email,
                    "Subject": subject,
                    "FromName": self._config.FROM_NAME
                },
                body=message.encode(),
                content_type=content_type
            ),
            routing_key=queue.name,
        )
