import uuid

from sqlalchemy import Column, UUID, VARCHAR, Enum, DateTime, func, ForeignKey, BIGINT
from sqlalchemy.orm import relationship

from src.db import Base

from src.models.state import ArticleState


class Article(Base):
    """
    The Article model
    """
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(VARCHAR(255), nullable=False)
    poster_url = Column(VARCHAR(255), nullable=True)
    content = Column(VARCHAR(32000), nullable=False)
    state = Column(Enum(ArticleState), default=ArticleState.DRAFT)
    views = Column(BIGINT(), nullable=False, default=0)
    owner_id = Column(UUID(as_uuid=True), nullable=False)
    likes = relationship("models.tables.like.Like", back_populates="article")
    tags = relationship('models.tables.tag.Tag', secondary='article_tags', back_populates='articles')
    comments_tree = relationship("models.tables.comment.CommentTree", back_populates="article")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'


class ArticleTag(Base):
    """
    Many-to-many table for Article and Tag
    """
    __tablename__ = "article_tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id"), nullable=False)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'
