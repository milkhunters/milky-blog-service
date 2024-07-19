import uuid
import datetime

from mbs.domain.models import Article, ArticleState, FileId, UserId


class ArticleService:

    def create_article(
            self,
            title: str,
            content: str,
            state: ArticleState,
            author_id: UserId,
            tags: list[str],
            poster: FileId = None
    ):
        return Article(
            id=uuid.uuid4(),
            title=title,
            poster=poster,
            content=content,
            state=state,
            views=0,
            likes=0,
            tags=tags,
            author_id=author_id,
            created_at=datetime.datetime.now(datetime.UTC),
            updated_at=None
        )

    def update_article(
            self,
            article: Article,
            title: str,
            content: str,
            state: ArticleState,
            poster: FileId | None,
            views: int,
            likes: int,
            tags: list[str]
    ):
        return Article(
            id=article.id,
            title=title,
            poster=poster,
            content=content,
            state=state,
            views=views,
            likes=likes,
            tags=tags,
            author_id=article.author_id,
            created_at=article.created_at,
            updated_at=datetime.datetime.now(datetime.UTC)
        )