import uuid

from src import NotificationType
from src import blog_service_control_pb2
from mbs.protos.blog_service_control import blog_service_control_pb2_grpc
from mbs.services.repository import NotificationRepo


class BlogService(blog_service_control_pb2_grpc.BlogServicer):
    def __init__(self, app_state):
        self.db_session = app_state.db_session

    async def SendNotification(self, request, context):
        try:

            owner_id = uuid.UUID(request.owner_id)
            content_id = uuid.UUID(request.content_id)
            content = request.content
            type_id = NotificationType(request.type_id)

            async with self.db_session() as session:
                notification_repo = NotificationRepo(session)
                resp = await notification_repo.create(
                    owner_id=owner_id,
                    type_id=type_id,
                    content_id=content_id,
                    content=content,
                )
                await session.commit()
        except Exception:  # todo: описать конкретные исключения
            return blog_service_control_pb2.NotificationReply(id="Error")
        return blog_service_control_pb2.NotificationReply(id=resp.id)
