import uuid
from typing import Literal

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src import get_services
from mbs.models import schemas
from src import ArticleState, RateState
from mbs.services import ServiceFactory
from mbs.views import ArticleResponse, ArticlesResponse
from mbs.views.article import ArticleFilesResponse, ArticleFileUploadResponse, ArticleFileResponse

router = APIRouter()


@router.get("/list", response_model=ArticlesResponse, status_code=http_status.HTTP_200_OK)
async def get_articles(
        page: int = 1,
        per_page: int = 10,
        order_by: Literal["title", "updated_at", "created_at"] = "created_at",
        query: str = None,
        state: ArticleState = ArticleState.PUBLISHED,
        owner_id: uuid.UUID = None,
        services: ServiceFactory = Depends(get_services)
):
    """
    Получить список статей

    Требуемое состояние: -

    Требуемые права доступа: GET_PUBLIC_ARTICLES / GET_PRIVATE_ARTICLES / GET_SELF_ARTICLES

    Если указан owner_id, то возвращаются только статьи этого пользователя,
    причем пользователь с доступом GET_PRIVATE_ARTICLES может просматривать чужие публикации.
    """
    return ArticlesResponse(
        content=await services.article.get_articles(page, per_page, order_by, query, state, owner_id)
    )


@router.post("/new", response_model=ArticleResponse, status_code=http_status.HTTP_201_CREATED)
async def new_article(article: schemas.ArticleCreate, services: ServiceFactory = Depends(get_services)):
    """
    Создать статью

    Требуемое состояние: ACTIVE

    Требуемые права доступа: CREATE_SELF_ARTICLES

    Максимальный размер статьи - 32000 символов
    """
    return ArticleResponse(content=await services.article.create_article(article))


@router.get("/{article_id}", response_model=ArticleResponse, status_code=http_status.HTTP_200_OK)
async def get_article(article_id: uuid.UUID, services: ServiceFactory = Depends(get_services)):
    """
    Получить статью по id

    Требуемое состояние: -

    Требуемые права доступа: GET_PUBLIC_ARTICLES / GET_PRIVATE_ARTICLES / GET_SELF_ARTICLES
    """
    return ArticleResponse(content=await services.article.get_article(article_id))


@router.put("/{article_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def update_article(
        article_id: uuid.UUID,
        data: schemas.ArticleUpdate,
        services: ServiceFactory = Depends(get_services)
):
    """
    Обновить статью по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_SELF_ARTICLES / UPDATE_USER_ARTICLES

    Причем пользователь с доступом UPDATE_USER_ARTICLES может редактировать чужие публикации.
    """
    await services.article.update_article(article_id, data)


@router.delete("/{article_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_article(article_id: uuid.UUID, services: ServiceFactory = Depends(get_services)):
    """
    Удалить статью по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: DELETE_SELF_ARTICLES / DELETE_USER_ARTICLES

    Причем пользователь с доступом DELETE_USER_ARTICLES может удалять чужие публикации.
    """
    await services.article.delete_article(article_id)


@router.post("/rate/{article_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def rate_article(article_id: uuid.UUID, state: RateState, services: ServiceFactory = Depends(get_services)):
    """
    Оценить статью по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: RATE_ARTICLES
    """
    await services.article.rate_article(article_id, state)


@router.get("/files/{article_id}", response_model=ArticleFilesResponse, status_code=http_status.HTTP_200_OK)
async def get_article_files(article_id: uuid.UUID, services: ServiceFactory = Depends(get_services)):
    """
    Получить список файлов статьи по id

    Требуемое состояние: -

    Требуемые права доступа: GET_PUBLIC_ARTICLES / GET_PRIVATE_ARTICLES / GET_SELF_ARTICLES
    """
    return ArticleFilesResponse(content=await services.article.get_article_files(article_id))


@router.get("/files/{article_id}/{file_id}", response_model=ArticleFileResponse, status_code=http_status.HTTP_200_OK)
async def get_article_file(
        article_id: uuid.UUID,
        file_id: uuid.UUID,
        download: bool = False,
        services: ServiceFactory = Depends(get_services)
):
    """
    Получить файл статьи по id

    Требуемое состояние: -

    Требуемые права доступа: GET_PUBLIC_ARTICLES / GET_PRIVATE_ARTICLES / GET_SELF_ARTICLES
    """
    return ArticleFileResponse(content=await services.article.get_article_file(article_id, file_id, download))


@router.post(
    "/files/{article_id}",
    response_model=ArticleFileUploadResponse,
    status_code=http_status.HTTP_200_OK
)
async def upload_article_file(
        article_id: uuid.UUID,
        data: schemas.ArticleFileCreate,
        services: ServiceFactory = Depends(get_services)
):
    """
    Загрузить файл статьи по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_SELF_ARTICLES / UPDATE_USER_ARTICLES

    Причем пользователь с доступом UPDATE_USER_ARTICLES может редактировать чужие публикации.
    """
    return ArticleFileUploadResponse(content=await services.article.upload_article_file(article_id, data))


@router.post("/files/{article_id}/{file_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def confirm_article_file(
        article_id: uuid.UUID,
        file_id: uuid.UUID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Подтвердить загрузку файла статьи по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_SELF_ARTICLES / UPDATE_USER_ARTICLES

    Причем пользователь с доступом UPDATE_USER_ARTICLES может редактировать чужие публикации.
    """
    await services.article.confirm_article_file_upload(article_id, file_id)


@router.delete("/files/{article_id}/{file_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_article_file(
        article_id: uuid.UUID,
        file_id: uuid.UUID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Удалить файл статьи по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_SELF_ARTICLES / UPDATE_USER_ARTICLES

    Причем пользователь с доступом UPDATE_USER_ARTICLES может редактировать чужие публикации.
    """
    await services.article.delete_article_file(article_id, file_id)


@router.post("/poster", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def set_poster(
        article_id: uuid.UUID,
        file_id: uuid.UUID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Установить постер статьи по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_SELF_ARTICLES / UPDATE_USER_ARTICLES

    Причем пользователь с доступом UPDATE_USER_ARTICLES может редактировать чужие публикации.
    """
    await services.article.set_article_poster(article_id, file_id)
