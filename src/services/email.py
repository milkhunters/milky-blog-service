import logging

from config import load_config
from utils.rabbitmq import RabbitMQ

config = load_config()


class EmailService:
    CONTENT_TYPE = "text/html"
    FROM_NAME = "MILKY-TEAM"

    async def send_mail(self, rabbitmq: RabbitMQ, email: str, subject: str, message: str):
        """
        Отправляет сообщение на почту

        :param email: почта пользователя.
        :param subject: тема сообщения
        :param message: текст сообщения
        :param rabbitmq: клиент rabbitmq

        """

        await rabbitmq.send(
            body=message,
            headers={
                "To": email,
                "Subject": subject,
                "FromName": self.FROM_NAME
            },
            routing_key=config.base.amqp.queue,
            content_type=self.CONTENT_TYPE
        )