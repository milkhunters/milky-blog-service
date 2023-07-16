import uuid
from typing import Literal

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src.dependencies.services import get_services
from src.models import schemas
from src.models.state import ArticleState
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
    return ArticlesResponse(
        content=await services.article.get_articles(page, per_page, order_by, query, state, owner_id)
    )


@router.post("/create", response_model=ArticleResponse, status_code=http_status.HTTP_201_CREATED)
async def create_article(article: schemas.ArticleCreate, services: ServiceFactory = Depends(get_services)):
    return ArticleResponse(content=await services.article.create_article(article))


@router.get("/{article_id}", response_model=ArticleResponse, status_code=http_status.HTTP_200_OK)
async def get_article(article_id: uuid.UUID, services: ServiceFactory = Depends(get_services)):
    return ArticleResponse(content=await services.article.get_article(article_id))


@router.post("/update/{article_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def update_article(
        article_id: uuid.UUID,
        data: schemas.ArticleUpdate,
        services: ServiceFactory = Depends(get_services)
):
    await services.article.update_article(article_id, data)


@router.delete("/delete/{article_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_article(article_id: uuid.UUID, services: ServiceFactory = Depends(get_services)):
    await services.article.delete_article(article_id)
