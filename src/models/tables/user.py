from tortoise import fields, models
from models.role import Role, MainRole as M, AdditionalRole as A
from models.state import UserStates


class User(models.Model):
    """
    The User model
    """

    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=30, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    articles: fields.ReverseRelation["Article"]
    first_name = fields.CharField(max_length=50, null=True)
    last_name = fields.CharField(max_length=50, null=True)
    comments: fields.ReverseRelation["Comment"]
    notifications: fields.ReverseRelation["Notification"]
    role_id = fields.IntField(default=Role(M.user, A.one))
    state = fields.IntEnumField(UserStates)
    hashed_password = fields.CharField(max_length=255)
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True, null=True)

    def full_name(self) -> str:
        if self.first_name or self.last_name:
            return f"{self.first_name or ''} {self.last_name or ''}".strip()
        return self.username

    class PydanticMeta:
        computed = ["full_name"]
        exclude = ["hashed_password"]


class UserDeleted(models.Model):
    id = fields.IntField(pk=True)
    delete_time = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user_deleted"
