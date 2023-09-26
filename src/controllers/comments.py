import uuid

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src.dependencies.services import get_services
from src.models import schemas
from src.services import ServiceFactory
from src.views.comment import CommentResponse, CommentsResponse

router = APIRouter()


@router.post("/create", response_model=CommentResponse, status_code=http_status.HTTP_201_CREATED)
async def create_comment(
        article_id: uuid.UUID,
        data: schemas.CommentCreate,
        parent_id: uuid.UUID = None,
        service: ServiceFactory = Depends(get_services)
):
    """
    Создать комментарий

    Требуемое состояние: ACTIVE

    Требуемые права доступа: CREATE_COMMENT
    """
    return CommentResponse(content=await service.comment.add_comment(article_id, data, parent_id))


@router.get("/list", response_model=CommentsResponse, status_code=http_status.HTTP_200_OK)
async def get_comments(article_id: uuid.UUID, service: ServiceFactory = Depends(get_services)):
    """
    Получить список комментариев публикации

    Требуемое состояние: -

    Требуемые права доступа: GET_PUBLIC_COMMENTS
    """
    return CommentsResponse(content=await service.comment.get_comments(article_id))


@router.get("/get", response_model=CommentResponse, status_code=http_status.HTTP_200_OK)
async def get_comment(comment_id: uuid.UUID, service: ServiceFactory = Depends(get_services)):
    """
    Получить комментарий

    Требуемое состояние: -

    Требуемые права доступа: GET_PUBLIC_COMMENTS / GET_DELETED_COMMENTS

    Пользователь с доступом GET_PUBLIC_COMMENTS может получить публичный комментарий

    Пользователь с доступом GET_DELETED_COMMENTS может получить удаленный комментарий
    """
    return CommentResponse(content=await service.comment.get_comment(comment_id))


@router.post("/update/{comment_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def update_comment(
        comment_id: uuid.UUID,
        data: schemas.CommentUpdate,
        service: ServiceFactory = Depends(get_services)
):
    """
    Обновить комментарий

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_USER_COMMENT / UPDATE_SELF_COMMENT

    Пользователь с доступом UPDATE_USER_COMMENT может обновить чужой комментарий

    Пользователь с доступом UPDATE_SELF_COMMENT может обновить свой комментарий не позднее 24 часов после создания
    """
    await service.comment.update_comment(comment_id, data)


@router.delete("/delete/{comment_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: uuid.UUID, service: ServiceFactory = Depends(get_services)):
    """
    Удалить комментарий

    Минимальная роль: USER.ONE

    Требуемое состояние: ACTIVE

    Требуемые права доступа: DELETE_USER_COMMENT / DELETE_SELF_COMMENT

    Пользователь с доступом DELETE_USER_COMMENT может удалить чужой комментарий

    Пользователь с доступом DELETE_SELF_COMMENT может удалить свой комментарий
    """
    await service.comment.delete_comment(comment_id)


@router.delete("/delete_all/{article_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_all_comments(article_id: uuid.UUID, service: ServiceFactory = Depends(get_services)):
    """
    Удалить все комментарии статьи

    Требуемое состояние: ACTIVE

    Требуемые права доступа: DELETE_USER_COMMENT
    """
    await service.comment.delete_all_comments(article_id)
