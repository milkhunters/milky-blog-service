import uuid

from sqlalchemy import Column, UUID, DateTime, func, ForeignKey, VARCHAR, BOOLEAN
from sqlalchemy.orm import relationship

from src.db import Base


class File(Base):
    """
    The ArticleFile model

    """
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(VARCHAR(255), nullable=False)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False)
    article = relationship("models.tables.article.Article", back_populates="files")
    content_type = Column(VARCHAR(255), nullable=False)
    is_uploaded = Column(BOOLEAN(), default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'
