import uuid
from datetime import datetime

from pydantic import BaseModel


class Tag(BaseModel):
    id: uuid.UUID
    title: str

    created_at: datetime

    class Config:
        orm_mode = True
