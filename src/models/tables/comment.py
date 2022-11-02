from tortoise import fields, models

from models.state import CommentState


class Comment(models.Model):
    """
    The Comment model

    """
    id = fields.IntField(pk=True)
    content = fields.TextField(max_length=1000, min_length=1)
    owner = fields.ForeignKeyField('models.User', related_name="comments")
    state = fields.IntEnumField(CommentState, default=CommentState.active)  # TODO: возможна ошибка из-за default=...
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True, null=True)


class CommentTree(models.Model):
    """
    The CommentSubset model
    («Closure Table» и «Adjacency List»)

    # Описание полей
    ancestor: предок
    descendant: потомок
    nearest_ancestor: ближайший предок
    article: пост
    level: уровень вложенности

    """
    ancestor_id = fields.IntField()
    descendant_id = fields.IntField()
    nearest_ancestor_id = fields.IntField()
    article = fields.ForeignKeyField('models.Article', related_name="comments_tree")
    level = fields.IntField()
    create_time = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "comment_tree"
