import math

import views
from exceptions import APIError
from models import schemas
from models.state import ArticleState
from services.repository import ArticleRepo, CommentRepo


class ArticleService:

    def __init__(
            self,
            article_repo: ArticleRepo = ArticleRepo(),

    ):
        self._repo = article_repo

    async def get_articles(
            self,
            page_num: int = 1,
            per_page: int = 10,
            order_by: str = "id",
            query: str = None
    ) -> views.ArticlesResponse:
        """
        Получить список статей
        (для меню)

        :param page_num: номер страницы (всегда >= 1)
        :param per_page: количество статей на странице (всегда >= 1 но <= per_page_limit)
        :param order_by: поле сортировки
        :param query: поисковый запрос (если необходим)
        :return:

        """

        if page_num < 1:
            raise APIError(919, "Номер страницы не может быть меньше 1")

        per_page_limit = 40

        # Подготовка входных данных
        order_by = order_by if order_by in ["id", "title", "create_time"] else "id"
        per_page = max(min(per_page, per_page_limit, 2147483646), 1)
        limit = min(page_num * per_page, 2147483646)
        skip = min((page_num - 1) * per_page, 2147483646)

        # поиск
        articles = await self._repo.search(
            query=query,
            fields=["title", "description", "content"],
            limit=limit + 1,
            skip=skip,
            order_by=order_by,
            state=ArticleState.PUBLISHED
        )

        return views.ArticlesResponse(
            items=[views.ArticleResponse.from_orm(article) for article in articles[:per_page]],
            current=page_num,
            next=(page_num + 1) if len(articles) > per_page else page_num,
            previous=(page_num - 1) if page_num > 1 else page_num
        )

    async def get_article(self, article_id: int) -> views.ArticleResponse:
        """
        Получить статью по id
        """
        article = await self._repo.get(id=article_id, fetch_related_fields=["owner"])
        if not article:
            raise APIError(919)
        return views.ArticleResponse.from_orm(article)



    async def create_article(self, article: schemas.ArticleCreate) -> views.ArticleResponse:
        pass

    async def update_article(self, article_id: int, article: schemas.ArticleUpdate) -> views.ArticleResponse:
        pass

    async def delete_article(self, article_id: int) -> views.ArticleResponse:
        pass
