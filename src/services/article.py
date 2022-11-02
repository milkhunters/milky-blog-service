import math

import views
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
            page: int = 1,
            per_page: int = 10,
            order_by: str = "id",
            query: str = None
    ) -> views.ArticlesResponse:
        """
        Получить список статей
        (для меню)

        :param page: номер страницы (всегда >= 1)
        :param per_page: количество статей на странице (всегда >= 1 но <= per_page_limit)
        :param order_by: поле сортировки
        :param query: поисковый запрос (если необходим)
        :return:

        TODO: переписать

        """

        per_page_limit = 100

        # Подготовка входных данных
        per_page = max(min(per_page, per_page_limit), 1)
        limit = page * per_page
        skip = (page - 1) * per_page

        # поиск
        articles = await self._repo.search(
            query=query,
            fields=["title", "description", "content"],
            limit=limit,
            skip=skip,
            order_by=order_by,
            state=ArticleState.PUBLISHED
        )

        # Подготовка выходных данных
        total_notifications = await self._db.get_count_of_articles(search, ArticleState.published)
        total_pages = math.ceil(max(total_notifications, 1) / per_page)

        #  TODO: сделать реализацию без полного кол-ва страниц,
        #   а с использованием next и previous:
        #   next_page высчитывать по средствам limit + 1 и проверять наличие следующей страницы

        return views.ArticlesResponse(
            items=[views.ArticleResponse.from_orm(article) for article in articles],
            current_page=page,
            total_pages=total_pages,
            next_page=(page + 1) if page < total_pages else page,
            previous_page=(page - 1) if page > 1 else page
        )

    async def get_article(self, article_id: int) -> views.ArticleResponse:
        pass

    async def create_article(self, article: schemas.ArticleCreate) -> views.ArticleResponse:
        pass

    async def update_article(self, article_id: int, article: schemas.ArticleUpdate) -> views.ArticleResponse:
        pass

    async def delete_article(self, article_id: int) -> views.ArticleResponse:
        pass
