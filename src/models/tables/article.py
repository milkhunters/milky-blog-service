import textwrap

from tortoise import fields, models

from models.data.articles import ArticleState


class Article(models.Model):
    """
    The Article model
    """

    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    poster_url = fields.CharField(max_length=255, null=True)
    content = fields.TextField()
    tags = fields.ManyToManyField('models.Tag', related_name="articles")
    owner = fields.ForeignKeyField('models.User', related_name="articles")
    state = fields.IntField(default=ArticleState.draft)
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True, null=True)

    @property
    def description(self):
        return textwrap.shorten(self.content, 100, placeholder="...")

    class PydanticMeta:
        computed = ["description"]
