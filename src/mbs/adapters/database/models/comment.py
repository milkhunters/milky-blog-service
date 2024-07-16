import uuid

from sqlalchemy import Column, UUID, VARCHAR, Enum, DateTime, func, ForeignKey, Integer, BigInteger
from sqlalchemy.orm import relationship

from mbs.db import Base

from mbs.domain.models import CommentState


class Comment(Base):
    """
    The Comment model

    """
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(VARCHAR(1000), nullable=False)
    state = Column(Enum(CommentState), default=CommentState.PUBLISHED)

    author_id = Column(UUID(as_uuid=True), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'


class CommentTree(Base):
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

    __tablename__ = "comment_tree"

    id = Column(UUID(), primary_key=True, autoincrement=True)
    ancestor_id = Column(UUID(as_uuid=True), nullable=False)
    descendant_id = Column(UUID(as_uuid=True), nullable=False)
    nearest_ancestor_id = Column(UUID(as_uuid=True), nullable=True)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False)
    article = relationship("models.models.article.Article", back_populates="comments_tree")
    level = Column(Integer())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'


class CommentFile(Base):
    """
    Many-to-many table for Comment and Files
    """
    __tablename__ = "comment_files"

    comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id"), nullable=False)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"), nullable=False)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'


class CommentLike(Base):
    """
    The CommentLike model

    """
    __tablename__ = "comment_likes"

    author_id = Column(UUID(as_uuid=True), nullable=False)
    comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id"), nullable=False)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'
