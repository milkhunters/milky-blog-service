import uuid
from typing import Literal

from mbs import exceptions
from mbs.models import schemas
from src import Permission
from mbs.models.auth import BaseUser
from src import ArticleState, UserState, RateState
from mbs.services.auth.filters import state_filter
from mbs.services.auth.filters import permission_filter
from mbs.services.repository import CommentTreeRepo, LikeRepo, FileRepo
from mbs.services.repository import CommentRepo
from mbs.services.repository import ArticleRepo
from mbs.services.repository import TagRepo
from mbs.utils.s3 import S3Storage


class ArticleApplicationService:

    def __init__(
            self,
            current_user: BaseUser,
            article_repo: ArticleRepo,
            tag_repo: TagRepo,
            comment_tree_repo: CommentTreeRepo,
            comment_repo: CommentRepo,
            like_repo: LikeRepo,
            file_repo: FileRepo,
            file_storage: S3Storage

    ):
        self._current_user = current_user
        self._repo = article_repo
        self._tag_repo = tag_repo
        self._tree_repo = comment_tree_repo
        self._comment_repo = comment_repo
        self._like_repo = like_repo
        self._file_repo = file_repo
        self._file_storage = file_storage

    async def get_articles(
            self,
            page: int = 1,
            per_page: int = 10,
            order_by: Literal["title", "updated_at", "created_at"] = "created_at",
            query: str = None,
            state: ArticleState = ArticleState.PUBLISHED,
            owner_id: uuid.UUID = None
    ) -> list[schemas.ArticleSmall]:
        """
        Получить список статей

        :param page: номер страницы (всегда >= 1)
        :param per_page: количество статей на странице (всегда >= 1, но <= per_page_limit)
        :param order_by: поле сортировки
        :param query: поисковый запрос (если необходим)
        :param state: статус статьи (по умолчанию только опубликованные)
        :param owner_id: id владельца статьи (если необходимо получить статьи только одного пользователя)
        :return:

        """

        if page < 1:
            raise exceptions.NotFound("Страница не найдена")
        if per_page < 1:
            raise exceptions.BadRequest("Неверное количество элементов на странице")

        if all(
                (
                        state != ArticleState.PUBLISHED,
                        owner_id != self._current_user.id,
                        Permission.GET_PRIVATE_ARTICLES.value not in self._current_user.permissions
                )
        ):
            raise exceptions.AccessDenied("Вы не можете получить список приватных статей")

        if all(
                (
                        state != ArticleState.PUBLISHED,
                        owner_id == self._current_user.id,
                        Permission.GET_SELF_ARTICLES.value not in self._current_user.permissions
                )
        ):
            raise exceptions.AccessDenied("Вы не можете получить свой список приватных статей")

        if all(
                (
                        state == ArticleState.PUBLISHED,
                        Permission.GET_PUBLIC_ARTICLES.value not in self._current_user.permissions
                )
        ):
            raise exceptions.AccessDenied("Вы не можете получить список опубликованных статей")

        per_page_limit = 40

        # Подготовка входных данных
        per_page = min(per_page, per_page_limit, 2147483646)
        offset = min((page - 1) * per_page, 2147483646)

        # Выполнение запроса
        if query:
            articles = await self._repo.search(
                query=query,
                fields=["title", "content"],
                limit=per_page,
                offset=offset,
                order_by=order_by,
                **{"state": state} if state else {},
                **{"owner_id": owner_id} if owner_id else {}
            )
        else:
            articles = await self._repo.get_all(
                limit=per_page,
                offset=offset,
                order_by=order_by,
                **{"state": state} if state else {},
                **{"owner_id": owner_id} if owner_id else {}
            )
        return [schemas.ArticleSmall.model_validate(article) for article in articles]

    async def get_article(self, article_id: uuid.UUID) -> schemas.Article:
        article = await self._repo.get(id=article_id)
        if not article:
            raise exceptions.NotFound("Статья не найдена")

        if all(
                (
                        article.state != ArticleState.PUBLISHED,
                        article.owner_id != self._current_user.id,
                        Permission.GET_PRIVATE_ARTICLES.value not in self._current_user.permissions
                )
        ):
            raise exceptions.AccessDenied("Материал не опубликован")

        if all(
                (
                        article.state != ArticleState.PUBLISHED,
                        article.owner_id == self._current_user.id,
                        Permission.GET_SELF_ARTICLES.value not in self._current_user.permissions
                )
        ):
            raise exceptions.AccessDenied("Вы не можете просматривать свои приватные публикации")

        if all(
                (
                        article.state == ArticleState.PUBLISHED,
                        Permission.GET_PUBLIC_ARTICLES.value not in self._current_user.permissions
                )
        ):
            raise exceptions.AccessDenied("Вы не можете просматривать публичные публикации")

        # Views
        if article.state == ArticleState.PUBLISHED and article.owner_id != self._current_user.id:
            article.views += 1
            await self._repo.session.commit()
            await self._repo.session.refresh(article)

        # Likes
        article.likes_count = await self._like_repo.count(article_id=article_id)

        return schemas.Article.model_validate(article)

    @permission_filter(Permission.CREATE_SELF_ARTICLES)
    @state_filter(UserState.ACTIVE)
    async def create_article(self, data: schemas.ArticleCreate) -> schemas.Article:
        _ = await self._repo.create(
            **data.model_dump(exclude_unset=True, exclude={"tags"}),
            owner_id=self._current_user.id
        )
        article = await self._repo.get(id=_.id)
        article.likes_count = 0
        # Добавление тегов
        for tag_title in data.tags:
            tag = await self._tag_repo.get(title=tag_title)
            if not tag:
                tag = await self._tag_repo.create(title=tag_title)
            article.tags.append(tag)
        await self._repo.session.commit()
        return schemas.Article.model_validate(article)

    @state_filter(UserState.ACTIVE)
    async def update_article(self, article_id: uuid.UUID, data: schemas.ArticleUpdate) -> None:
        article = await self._repo.get(id=article_id)
        if not article:
            raise exceptions.NotFound("Статья не найдена")

        if (
                article.owner_id != self._current_user.id and
                Permission.UPDATE_USER_ARTICLES.value not in self._current_user.permissions
        ):
            raise exceptions.AccessDenied("Вы не являетесь владельцем статьи")

        if (
                article.owner_id == self._current_user.id and
                Permission.UPDATE_SELF_ARTICLES.value not in self._current_user.permissions
        ):
            raise exceptions.AccessDenied("Вы не можете редактировать свои статьи")

        if data.tags:
            article.tags = []
            for tag_title in data.tags:
                tag = await self._tag_repo.get(title=tag_title)
                if not tag:
                    tag = await self._tag_repo.create(title=tag_title)
                article.tags.append(tag)
            await self._repo.session.commit()

        await self._repo.update(article_id, **data.model_dump(exclude_unset=True, exclude={"tags"}))

    @permission_filter(Permission.RATE_ARTICLES)
    @state_filter(UserState.ACTIVE)
    async def rate_article(self, article_id: uuid.UUID, state: RateState) -> None:
        article = await self._repo.get(id=article_id)
        if not article:
            raise exceptions.NotFound("Статья не найдена")

        if article.owner_id == self._current_user.id:
            raise exceptions.BadRequest("Вы не можете оценивать свои статьи")

        like = await self._like_repo.get(article_id=article_id, owner_id=self._current_user.id)
        if state == RateState.LIKE:
            if like:
                raise exceptions.BadRequest("Вы уже поставили лайк")
            await self._like_repo.create(article_id=article_id, owner_id=self._current_user.id)
        elif state == RateState.NEUTRAL:
            if not like:
                raise exceptions.BadRequest("Вы еще не оценили статью")
            await self._like_repo.delete(like.id)

    @state_filter(UserState.ACTIVE)
    async def delete_article(self, article_id: uuid.UUID) -> None:
        article = await self._repo.get(id=article_id)
        if not article:
            raise exceptions.NotFound("Статья не найдена")

        if (
                article.owner_id != self._current_user.id and
                Permission.DELETE_USER_ARTICLES.value not in self._current_user.permissions
        ):
            raise exceptions.AccessDenied("Вы не являетесь владельцем статьи")

        if (
                article.owner_id == self._current_user.id and
                Permission.DELETE_SELF_ARTICLES.value not in self._current_user.permissions
        ):
            raise exceptions.AccessDenied("Вы не можете удалять свои статьи")

        await self._repo.delete(id=article_id)
        await self._comment_repo.delete_comments_by_article(article_id)

    async def get_article_files(self, article_id: uuid.UUID) -> list[schemas.ArticleFileItem]:
        article = await self._repo.get(id=article_id)
        if not article:
            raise exceptions.NotFound("Статья не найдена")

        if all(
                (
                        article.state != ArticleState.PUBLISHED,
                        article.owner_id != self._current_user.id,
                        Permission.GET_PRIVATE_ARTICLES.value not in self._current_user.permissions
                )
        ):
            raise exceptions.AccessDenied("Вы не можете просматривать файлы неопубликованных статей")

        if all(
                (
                        article.state != ArticleState.PUBLISHED,
                        article.owner_id == self._current_user.id,
                        Permission.GET_SELF_ARTICLES.value not in self._current_user.permissions
                )
        ):
            raise exceptions.AccessDenied("Вы не можете просматривать файлы своих приватных публикаций")

        if all(
                (
                        article.state == ArticleState.PUBLISHED,
                        Permission.GET_PUBLIC_ARTICLES.value not in self._current_user.permissions
                )
        ):
            raise exceptions.AccessDenied("Вы не можете просматривать файлы публичных публикаций")

        resp = []

        files = await self._file_repo.get_all(article_id=article_id, is_uploaded=True)

        for file in files:
            url = self._file_storage.generate_download_public_url(
                file_path=f"{article.id}/{file.id}",
                content_type=file.content_type,
                rcd="inline",
                filename=file.filename
            )
            resp.append(schemas.ArticleFileItem(
                url=url,
                **schemas.ArticleFile.model_validate(file).model_dump(exclude={"is_uploaded", "article_id"})
            ))

        return resp

    async def get_article_file(
            self,
            article_id: uuid.UUID,
            file_id: uuid.UUID,
            download: bool
    ) -> schemas.ArticleFileItem:

        article = await self._repo.get(id=article_id)
        if not article:
            raise exceptions.NotFound("Статья не найдена")

        if all(
                (
                        article.state != ArticleState.PUBLISHED,
                        article.owner_id != self._current_user.id,
                        Permission.GET_PRIVATE_ARTICLES.value not in self._current_user.permissions
                )
        ):
            raise exceptions.AccessDenied("Вы не можете просматривать файлы неопубликованных статей")

        if all(
                (
                        article.state != ArticleState.PUBLISHED,
                        article.owner_id == self._current_user.id,
                        Permission.GET_SELF_ARTICLES.value not in self._current_user.permissions
                )
        ):
            raise exceptions.AccessDenied("Вы не можете просматривать файлы своих приватных публикаций")

        if all(
                (
                        article.state == ArticleState.PUBLISHED,
                        Permission.GET_PUBLIC_ARTICLES.value not in self._current_user.permissions
                )
        ):
            raise exceptions.AccessDenied("Вы не можете просматривать файлы публичных публикаций")

        file = await self._file_repo.get(id=file_id)
        if not file:
            raise exceptions.NotFound("Файл не найден")

        if not file.is_uploaded:
            raise exceptions.NotFound("Файл не загружен")

        url = self._file_storage.generate_download_public_url(
            file_path=f"{article.id}/{file.id}",
            content_type=file.content_type,
            rcd="attachment" if download else "inline",
            filename=file.filename
        )

        return schemas.ArticleFileItem(
            url=url,
            **schemas.ArticleFile.model_validate(file).model_dump(exclude={"is_uploaded", "article_id"})
        )

    @state_filter(UserState.ACTIVE)
    async def upload_article_file(
            self,
            article_id: uuid.UUID,
            data: schemas.ArticleFileCreate
    ) -> schemas.ArticleFileUpload:

        article = await self._repo.get(id=article_id)
        if not article:
            raise exceptions.NotFound("Статья не найдена")

        if article.state == ArticleState.DELETED:
            raise exceptions.BadRequest("Вы не можете загружать файлы для статей, которые были удалены")

        if (
                article.owner_id != self._current_user.id and
                Permission.UPDATE_USER_ARTICLES.value not in self._current_user.permissions
        ):
            raise exceptions.AccessDenied("Вы не являетесь владельцем статьи")

        if (
                article.owner_id == self._current_user.id and
                Permission.UPDATE_SELF_ARTICLES.value not in self._current_user.permissions
        ):
            raise exceptions.AccessDenied("Вы не можете редактировать свои статьи")

        file = await self._file_repo.create(
            filename=data.filename,
            article_id=article_id,
            content_type=data.content_type.value
        )

        url = schemas.PreSignedPostUrl.model_validate(
            await self._file_storage.generate_upload_url(
                file_path=f"{article.id}/{file.id}",
                content_type=data.content_type.value,
                content_length=(1, 100 * 1024 * 1024),  # 100mb
                expires_in=30 * 60  # 30 min
            )
        )

        return schemas.ArticleFileUpload(
            file_id=file.id,
            upload_url=url
        )

    @state_filter(UserState.ACTIVE)
    async def confirm_article_file_upload(
            self,
            article_id: uuid.UUID,
            file_id: uuid.UUID
    ) -> None:

        article = await self._repo.get(id=article_id)
        if not article:
            raise exceptions.NotFound("Статья не найдена")

        if article.state == ArticleState.DELETED:
            raise exceptions.BadRequest("Вы не можете подтверждать файлы для статей, которые были удалены")

        if (
                article.owner_id != self._current_user.id and
                Permission.UPDATE_USER_ARTICLES.value not in self._current_user.permissions
        ):
            raise exceptions.AccessDenied("Вы не являетесь владельцем статьи")

        if (
                article.owner_id == self._current_user.id and
                Permission.UPDATE_SELF_ARTICLES.value not in self._current_user.permissions
        ):
            raise exceptions.AccessDenied("Вы не можете подтверждать загрузку файлов")

        file = await self._file_repo.get(id=file_id)
        if not file:
            raise exceptions.NotFound("Файл не найден")

        if file.article_id != article_id:
            raise exceptions.BadRequest("Файл не принадлежит статье")

        if file.is_uploaded:
            raise exceptions.BadRequest("Файл уже загружен")

        info = await self._file_storage.info(file_path=f"{article_id}/{file_id}")
        if not info:
            raise exceptions.NotFound("Файл не загружен")

        await self._file_repo.update(id=file_id, is_uploaded=True)

    @state_filter(UserState.ACTIVE)
    async def delete_article_file(self, article_id: uuid.UUID, file_id: uuid.UUID) -> None:
        article = await self._repo.get(id=article_id)
        if not article:
            raise exceptions.NotFound("Статья не найдена")

        if article.state == ArticleState.DELETED:
            raise exceptions.BadRequest("Вы не можете удалять файлы статей, которые были удалены")

        if (
                article.owner_id != self._current_user.id and
                Permission.UPDATE_USER_ARTICLES.value not in self._current_user.permissions
        ):
            raise exceptions.AccessDenied("Вы не являетесь владельцем статьи")

        if (
                article.owner_id == self._current_user.id and
                Permission.UPDATE_SELF_ARTICLES.value not in self._current_user.permissions
        ):
            raise exceptions.AccessDenied("Вы не можете удалять файлы")

        file = await self._file_repo.get(id=file_id)
        if not file:
            raise exceptions.NotFound("Файл не найден")

        if file.article_id != article_id:
            raise exceptions.BadRequest("Файл не принадлежит статье")

        if not file.is_uploaded:
            raise exceptions.BadRequest("Файл не загружен")

        if article.poster == file_id:
            await self._repo.update(id=article_id, poster=None)

        await self._file_storage.delete(file_path=f"{article_id}/{file_id}")
        await self._file_repo.delete(id=file_id)

    @state_filter(UserState.ACTIVE)
    async def set_article_poster(self, article_id: uuid.UUID, file_id: uuid.UUID) -> None:
        article = await self._repo.get(id=article_id)
        if not article:
            raise exceptions.NotFound("Статья не найдена")

        if article.state == ArticleState.DELETED:
            raise exceptions.BadRequest("Вы не можете устанавливать постер для статей, которые были удалены")

        if (
                article.owner_id != self._current_user.id and
                Permission.UPDATE_USER_ARTICLES.value not in self._current_user.permissions
        ):
            raise exceptions.AccessDenied("Вы не являетесь владельцем статьи")

        if (
                article.owner_id == self._current_user.id and
                Permission.UPDATE_SELF_ARTICLES.value not in self._current_user.permissions
        ):
            raise exceptions.AccessDenied("Вы не можете установить постер для своих статей")

        file = await self._file_repo.get(id=file_id)
        if not file:
            raise exceptions.NotFound("Файл не найден")

        if file.article_id != article_id:
            raise exceptions.BadRequest("Файл не принадлежит статье")

        if not file.is_uploaded:
            raise exceptions.BadRequest("Файл не загружен")

        if article.poster == file_id:
            raise exceptions.BadRequest("Этот файл уже является постером статьи")

        await self._repo.update(id=article_id, poster=file_id)
