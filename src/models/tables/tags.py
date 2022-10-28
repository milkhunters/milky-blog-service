from tortoise import fields, models
from .article import Article


class Tag(models.Model):
    """
    The Tag model

    Общая модель для тегов
    """

    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=30)
    articles: fields.ReverseRelation["Article"]
    create_time = fields.DatetimeField(auto_now_add=True)
