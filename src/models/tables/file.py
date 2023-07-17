import uuid

from sqlalchemy import Column, ForeignKey, VARCHAR, DateTime, func, Enum

from sqlalchemy import UUID
from sqlalchemy.orm import relationship

from src.db import Base
from src.models.file_type import FileType


class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(VARCHAR(255), default="file")
    content_type = Column(Enum(FileType), nullable=False)

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner = relationship("models.tables.user.User", back_populates="files")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'
