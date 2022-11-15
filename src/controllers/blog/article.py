from fastapi import APIRouter, Depends
from fastapi import Request

from dependencies.jwt_barrier import JWTCookie
from dependencies.role_filter import RoleFilter
from models.state import ArticleState
from models.state import CommentState
from services import BlogService
from services.comment import CommentService
from exceptions import APIError

from models import schemas
from models.role import Role, MainRole as M, AdditionalRole as A
import views

router = APIRouter()


@router.get(
    "/get",
    summary="Получение публикации",
    description="Используется для получения полных данных публикации, включая комментарии",
    response_model=views.ArticleResponse,
)
async def get_article(
        id: int,
        request: Request,
        auth=Depends(JWTCookie(auto_error=False))
):
    """
    Получение данных одной публикации.
    :param id: Идентификатор публикации
    :param auth
    :param request:
    :return:

    TODO: возможно стоит вынести логику проверок
    """
    article = await BlogService().get_article(id)
    if article.state != ArticleState.published:
        if auth and request.user.id != article.owner.id:
            raise APIError(918)
        return article
    return article


@router.get("/list", response_model=views.ArticlesResponse, summary="Получение публикаций")
async def get_list(page: int = 1, per_page: int = 10, order_by: str = "id", query: str = None):
    """
    Получение списка публикаций
    (меньше данных)
    """
    return await BlogService().get_articles(page, per_page, order_by, query, ArticleState.PUBLISHED)


@router.get(
    "/my",
    response_model=views.ArticlesResponse,
    summary="Получение публикаций пользователя",
    dependencies=[Depends(JWTCookie())]
)
async def my(
        request: Request,
        page: int = 1,
        per_page: int = 10,
        order_by: str = "id",
        query: str = None,
        state: ArticleState = None
):
    """
    Получение списка публикаций пользователя
    (меньше данных)
    """
    return await BlogService().get_articles(page, per_page, order_by, query, state, request.user.id)


@router.post(
    "/create",
    summary="Создание публикации",
    response_model=views.ArticleResponse,
    dependencies=[Depends(JWTCookie()), Depends(RoleFilter(Role(M.moderator, A.one)))],
)
async def create_article(article: schemas.ArticleCreate, request: Request):
    """
    Создание публикации.

    :param article:
    :param request
    :return:
    """
    return await BlogService().create_article(article, request.user.id)


@router.post(
    "/update",
    response_model=views.ArticleResponse,
    dependencies=[Depends(JWTCookie())],
    summary="Обновление публикации"
)
async def update_article(id: int, data: schemas.ArticleUpdate):
    """
    Обновление публикации

    :param id ид публикации
    :param data:
    :return:

    TODO: реализовать
    """
    # TODO: исправить: нет проверки на автора
    return await BlogService().update_article(id, data)


@router.delete(
    "/delete",
    dependencies=[Depends(JWTCookie())],
    summary="Удаление публикации"
)
async def delete_article(id: int):
    """
    Удаление публикации

    Состояние публикации становится deleted,
    Ветка комментариев и сами комментарии удаляются.
    :param id: id публикации
    :return:

    TODO: реализовать
    """
    await BlogService().delete_article(id)
