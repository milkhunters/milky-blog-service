
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

type TagId = UUID

class Tag(BaseModel):
    id: TagId
    title: str

    created_at: datetime
