import uuid
import datetime

from mbs.domain.models import Tag


class TagService:

    def create_tag(self, title: str):
        return Tag(
            id=uuid.uuid4(),
            title=title,
            created_at=datetime.datetime.now(datetime.UTC)
        )
