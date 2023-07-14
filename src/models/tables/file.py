import uuid

from sqlalchemy import Column, ForeignKey, VARCHAR

from sqlalchemy import UUID
from sqlalchemy.orm import relationship

from src.db import Base


class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(VARCHAR(255), default="file")

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner = relationship("models.tables.user.User", back_populates="files")

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'
