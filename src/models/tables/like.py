import uuid

from sqlalchemy import Column, UUID, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

from src.db import Base


class Like(Base):
    """
    The Like model

    """
    __tablename__ = "likes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), nullable=False)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False)
    article = relationship("models.tables.article.Article", back_populates="likes")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'
