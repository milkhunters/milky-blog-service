from tortoise import fields, models

from models.state import NotificationTypes


class Notification(models.Model):
    """
    The Notification model

    """

    id = fields.IntField(pk=True, index=True)
    type = fields.IntEnumField(NotificationTypes)
    data = fields.IntField()
    owner = fields.ForeignKeyField('models.User', related_name="notifications")
    is_read = fields.BooleanField(default=False)
    create_time = fields.DatetimeField(auto_now_add=True)
