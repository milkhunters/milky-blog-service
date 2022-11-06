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


# TODO: переписать


@router.post(
    "/create",
    response_model=int,
    dependencies=[Depends(JWTCookie())],
    summary="Создание комментария"
)
async def create_comment(article_id: int, content: str, request: Request, answer_to: int = 0):
    """
    Создание комментария

    :param article_id: id публикации
    :param content: комментарий
    :param request:
    :param answer_to: ответ
    :return: int - id созданного комментария

    TODO: Реализовать

    """
    blog = BlogService()
    # Проверка получателя
    if answer_to != 0:
        recipient = await blog.get_comment(answer_to)
        if not recipient:
            raise APIError(919)
        if recipient["state"] != 1:
            raise APIError(909)
    # Проверка статьи
    article = await blog.get_article(id=article_id)
    if not article:
        raise APIError(919)
    # Выполнение
    new_comment = await blog.add_comment(article_id, content, request.user.id, answer_to)
    return new_comment.id


@router.get("/get_list", response_model=list[views.CommentResponse], summary="Получение комментариев публикации")
async def get_comments(article_id: int):
    """
    Получить комментарии публикации

    :param article_id: ид публикации
    :return:
    """
    return await BlogService().get_comments(article_id)


@router.get("/get", response_model=views.CommentResponse, summary="Получение комментария публикации")
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


@router.post("/update", dependencies=[Depends(JWTCookie())], summary="Обновление комментария")
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


@router.delete("/delete", dependencies=[Depends(JWTCookie())],
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
