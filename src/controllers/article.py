import uuid
from typing import Literal

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src.dependencies.services import get_services
from src.models import schemas
from src.models.state import ArticleState, RateState
from src.services import ServiceFactory
from src.views import ArticleResponse, ArticlesResponse

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

    Требуемые права доступа: CAN_GET_PUBLIC_ARTICLES / CAN_GET_PRIVATE_ARTICLES / CAN_GET_SELF_ARTICLES

    Если указан owner_id, то возвращаются только статьи этого пользователя,
    причем пользователь с доступом CAN_GET_PRIVATE_ARTICLES может просматривать чужие публикации.
    """
    return ArticlesResponse(
        content=await services.article.get_articles(page, per_page, order_by, query, state, owner_id)
    )


@router.post("/new", response_model=ArticleResponse, status_code=http_status.HTTP_201_CREATED)
async def new_article(article: schemas.ArticleCreate, services: ServiceFactory = Depends(get_services)):
    """
    Создать статью

    Требуемое состояние: ACTIVE

    Требуемые права доступа: CAN_CREATE_SELF_ARTICLES

    Максимальный размер статьи - 32000 символов
    """
    return ArticleResponse(content=await services.article.create_article(article))


@router.get("/{article_id}", response_model=ArticleResponse, status_code=http_status.HTTP_200_OK)
async def get_article(article_id: uuid.UUID, services: ServiceFactory = Depends(get_services)):
    """
    Получить статью по id

    Требуемое состояние: -

    Требуемые права доступа: CAN_GET_PUBLIC_ARTICLES / CAN_GET_PRIVATE_ARTICLES / CAN_GET_SELF_ARTICLES
    """
    return ArticleResponse(content=await services.article.get_article(article_id))


@router.post("/update/{article_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def update_article(
        article_id: uuid.UUID,
        data: schemas.ArticleUpdate,
        services: ServiceFactory = Depends(get_services)
):
    """
    Обновить статью по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: CAN_UPDATE_SELF_ARTICLES / CAN_UPDATE_USER_ARTICLES

    Причем пользователь с доступом CAN_UPDATE_USER_ARTICLES может редактировать чужие публикации.
    """
    await services.article.update_article(article_id, data)


@router.delete("/delete/{article_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_article(article_id: uuid.UUID, services: ServiceFactory = Depends(get_services)):
    """
    Удалить статью по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: CAN_DELETE_SELF_ARTICLES / CAN_DELETE_USER_ARTICLES

    Причем пользователь с доступом CAN_DELETE_USER_ARTICLES может удалять чужие публикации.
    """
    await services.article.delete_article(article_id)


@router.post("/rate/{article_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def rate_article(article_id: uuid.UUID, state: RateState, services: ServiceFactory = Depends(get_services)):
    """
    Оценить статью по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: CAN_RATE_ARTICLES
    """
    await services.article.rate_article(article_id, state)
