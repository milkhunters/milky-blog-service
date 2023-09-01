import uuid

from sqlalchemy import Column, UUID, VARCHAR, Enum, DateTime, func

from src.db import Base
from src.models.state import NotificationType


class Notification(Base):
    """
    The Notification model

    """
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(NotificationType), default=NotificationType.COMMENT_ANSWER)
    content_id = Column(UUID(as_uuid=True), nullable=False)
    content = Column(VARCHAR(64), nullable=False)
    owner_id = Column(UUID(as_uuid=True), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'
