import math

from models import schemas
from models.state import ArticleState
from services.repository import ArticleRepo


class ArticleService(ArticleRepo):

    async def get_articles(
            self,
            page: int = 1,
            per_page: int = 10,
            order_by: str = "id",
            queryset: str = None
    ) -> schemas.ArticlesOutMenu:
        """
        Получить список статей
        (для меню)

        :param page: номер страницы (всегда >= 1)
        :param per_page: количество статей на странице (всегда >= 1 но <= per_page_limit)
        :param order_by: поле сортировки
        :param queryset: поисковый запрос (если необходим)
        :return:

        TODO: переписать

        """

        per_page_limit = 100

        # Подготовка входных данных
        per_page = max(min(per_page, per_page_limit), 1)
        limit = page * per_page
        skip = (page - 1) * per_page

        # поиск
        if queryset:
            articles = await self._db.get_articles_by_search(queryset, skip, limit, order_by, ArticleState.published)
        else:
            articles = await self._db.get_articles(skip, limit, order_by, ArticleState.published)

        # Подготовка выходных данных
        total_notifications = await self._db.get_count_of_articles(search, ArticleState.published)
        total_pages = math.ceil(max(total_notifications, 1) / per_page)
        next_page = (page + 1) if page < total_pages else page
        previous_page = (page - 1) if page > 1 else page

        return schemas.ArticlesOutMenu(
            items=[schemas.ArticleOutMenu.from_orm(article) for article in articles],
            current_page=page,
            total_pages=total_pages,
            next_page=next_page,
            previous_page=previous_page
        )
