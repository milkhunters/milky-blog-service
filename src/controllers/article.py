from fastapi import APIRouter, Depends
from fastapi import Request

from dependencies.jwt_barrier import JWTCookie
from dependencies.role_filter import RoleFilter
from models.state import ArticleState
from models.state import CommentState
from src.services import ArticleService
from services.comment import CommentService
from exceptions import APIError

from models import schemas
from models.role import Role, MainRole as M, AdditionalRole as A
import views

router = APIRouter(tags=["Article"], prefix="/article")


@router.get("/get_list", response_model=views.ArticlesResponse, summary="Получение публикаций")
async def get_list(page: int = 1, per_page: int = 10, order_by: str = "id", search: str = None):
    """
    Получение списка публикаций
    (меньше данных)
    """
    return await ArticleService().get_articles(page, per_page, order_by, search)


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
    article = await ArticleService().get_article(id)
    if article.state != ArticleState.published:
        if auth and request.user.id != article.owner.id:
            raise APIError(918)
        return article
    return article


@router.post(
    "/create",
    summary="Создание публикации",
    response_model=views.ArticleResponse,
    dependencies=[Depends(JWTCookie()), Depends(RoleFilter(Role(M.moderator, A.one)))],
)
async def create_article(article: schemas.ArticleCreate):
    """
    Создание публикации.

    :param article:
    :return:
    """
    return await ArticleService().create_article(article)


@router.post(
    "/update",
    response_model=views.ArticleResponse,
    dependencies=[Depends(JWTCookie()), Depends(RoleFilter(21))],
    summary="Обновление публикации")
async def update_article(id: int, data: schemas.ArticleUpdate):
    """
    Обновление публикации

    :param id ид публикации
    :param data:
    :return:

    TODO: реализовать
    """
    article = await crud.get_article(id=id)
    if not article:
        raise APIError(919)
    await crud.update_article(article, data.dict(exclude_unset=True))
    return article


@router.delete("/deleteArticle",
               dependencies=[Depends(JWTCookie()), Depends(MinRoleFilter(21))],
               summary="Удаление публикации")
async def delete_article(id: int):
    """
    Удаление публикации

    Состояние публикации становится deleted,
    Ветка комментариев и сами комментарии удаляются.
    :param id: id публикации
    :return:

    TODO: реализовать
    """
    # Логика удаления статьи
    article = await crud.get_article(id=id)
    if not article:
        raise APIError(919)
    await crud.update_article(article, {"state": ArticleState.deleted})
    # Логика удаления комментариев статьи
    await CommentService().delete_all_comments(id)


@router.post("/createComment",
             response_model=int,
             dependencies=[Depends(JWTCookie())],
             summary="Создание комментария")
async def create_comment(article_id: int, content: str, request: Request, answer_to: int = 0):
    """
    Создание комментария

    :param article_id: id публикации
    :param content: комментарий
    :param request:
    :param answer_to: ответ
    :return: int - id созданного комментария

    """
    cs = CommentService()
    # Проверка получателя
    if answer_to != 0:
        recipient = await cs.get_comment(answer_to)
        if not recipient:
            raise APIError(919)
        if recipient["state"] != 1:
            raise APIError(909)
    # Проверка статьи
    article = await crud.get_article(id=article_id)
    if not article:
        raise APIError(919)
    # Выполнение
    new_comment = await cs.add_comment(article_id, content, request.user.id, answer_to)
    return new_comment.id


@router.get("/getComments", response_model=list[schemas.CommentOut], summary="Получение комментариев публикации")
async def get_comments(article_id: int):
    """
    Получить комментарии публикации

    :param article_id: ид публикации
    :return:
    """
    comments = await CommentService().get_comments(article_id)
    return [schemas.CommentOut(**comment) for comment in comments]


@router.get("/getComment", response_model=schemas.CommentOut, summary="Получение комментария публикации")
async def get_comment(id: int):
    """
    Получить комментарий

    :param id: ид комментария
    :return:
    """
    comment = await CommentService().get_comment(id)
    if not comment:
        raise APIError(919)
    return schemas.CommentOut(**comment)


@router.post("/updateComment", dependencies=[Depends(JWTCookie())], summary="Обновление комментария")
async def update_comment(id: int, content: str, request: Request):
    """
    Обновление комментария

    :param id: id комментария
    :param content: новый текст комментария
    :param request:
    :return:
    """
    cs = CommentService()

    comment = await cs.get_comment(id)
    if not comment or (comment["state"] == CommentState.deleted):
        raise APIError(919)
    if comment["owner_id"] != request.user.id:
        raise APIError(909)
    await cs.update_comment(id, content)


@router.delete("/deleteComment", dependencies=[Depends(JWTCookie())],
               summary="Удаление комментария")
async def delete_comment(id: int, request: Request):
    """
    Удаление комментария

    :param id: id комментария
    :param request
    :return:
    """
    cs = CommentService()
    # Проверки
    comment = await cs.get_comment(id)
    if not comment:
        raise APIError(919)
    if comment["state"] == CommentState.deleted:
        raise APIError(919)
    if comment["owner_id"] != request.user.id:
        if request.user.role_id < 21:
            raise APIError(909)
    # Выполнение
    await cs.delete_comment(id)
