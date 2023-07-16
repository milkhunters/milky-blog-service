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
    return CommentResponse(content=await service.comment.add_comment(article_id, data, parent_id))


@router.get("/list", response_model=CommentsResponse, status_code=http_status.HTTP_200_OK)
async def get_comments(article_id: uuid.UUID, service: ServiceFactory = Depends(get_services)):
    return CommentsResponse(content=await service.comment.get_comments(article_id))


@router.get("/get", response_model=CommentResponse, status_code=http_status.HTTP_200_OK)
async def get_comment(comment_id: uuid.UUID, service: ServiceFactory = Depends(get_services)):
    return CommentResponse(content=await service.comment.get_comment(comment_id))


@router.post("/update/{comment_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def update_comment(
        comment_id: uuid.UUID,
        data: schemas.CommentUpdate,
        service: ServiceFactory = Depends(get_services)
):
    await service.comment.update_comment(comment_id, data)


@router.delete("/delete/{comment_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: uuid.UUID, service: ServiceFactory = Depends(get_services)):
    await service.comment.delete_comment(comment_id)


@router.delete("/delete_all/{article_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_all_comments(article_id: uuid.UUID, service: ServiceFactory = Depends(get_services)):
    """
    Администратор может удалить все комментарии статьи

    """
    await service.comment.delete_all_comments(article_id)
