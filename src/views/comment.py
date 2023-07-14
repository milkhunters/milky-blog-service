from .base import BaseView
from src.models import schemas


class CommentResponse(BaseView):
    content: schemas.Comment
