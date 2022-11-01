from typing import TypeVar, Generic, List, Union, Optional

from tortoise.expressions import Q
from tortoise.fields import CharField, IntField

T = TypeVar('T')
S = TypeVar('S')


class BaseRepo(Generic[T, S]):
    def __init__(self):
        self.table = T

    async def get(self, query: str = None, *args, **kwargs) -> Optional[S]:
        return await self.table.get_or_none(**kwargs)

    async def search(
            self,
            query: Optional[str] = None,
            fields: Optional[list[str]] = None,
            limit: int = 40,
            offset: int = 0,
            order_by: Optional[str] = "id",
            fetch_related_fields: Optional[list[str]] = None,
            **kwargs
    ) -> Optional[List[S]]:
        """
        :param query: поисковый запрос
        :param fields: список полей, по которым будет производиться поиск
        :param limit: максимальное количество возвращаемых записей
        :param offset: смещение от начала списка
        :param order_by: поле, по которому будет производиться сортировка
        :param fetch_related_fields: список полей, которые будут загружены вместе с основной записью
        :param kwargs: дополнительные условия для фильтрации

        Пример:

        >>> await self.search(query="test", fields=["name", "email"], limit=10, offset=0, order_by="id")

        >>> await self.search(query="test", fields=["name", "email"], limit=10, offset=0, order_by="id", is_active=True)

        >>> await self.search(is_active=True)

        >>> await self.search(first_name="test", last_name="test")

        >>> await self.search()
        """
        qs = Q()
        queries: list[Q] = []
        kwargs_queries = [Q(**{f"{key}": value}) for key, value in kwargs.items()]
        if query:
            queryset = query.split(' ')  # Todo: нормалайзер

            if not fields:
                fields = [f.model_field_name for f in self.table._meta.fields_map.values() if isinstance(f, CharField)]

            search_queries = [Q(**{f"{field}__search": " | ".join(queryset)}) for field in fields]
            icontains_queries = []
            for query in queryset:
                icontains_queries += [Q(**{f"{field}__icontains": query}) for field in fields]

            queries += search_queries + icontains_queries
        queries += kwargs_queries

        for query in queries:
            qs |= query

        result = await self.table.filter(qs).limit(limit).offset(offset).order_by(order_by)
        if not result:
            return None

        if fetch_related_fields:
            await self.table.fetch_for_list(result, *fetch_related_fields)

        return S.from_orm(result)  # TODO: протестировать

    async def count(self, **kwargs) -> int:
        return await self.table.filter(**kwargs).count()

    async def insert(self, **kwargs) -> S:
        return await self.table.create(**kwargs)

    async def update(self, id: int, **kwargs) -> None:
        await self.table.filter(id=id).update(**kwargs)

    async def delete(self, id: int) -> None:
        await self.table.filter(id=id).delete()
