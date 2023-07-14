from fastapi import Depends
from fastapi.requests import Request
from fastapi.websockets import WebSocket

from src.dependencies.repos import get_repos
from src.services import ServiceFactory
from src.services.repository import RepoFactory


async def get_services(
        request: Request = None,
        websocket: WebSocket = None,
        repos: RepoFactory = Depends(get_repos)
) -> ServiceFactory:
    if request:
        app = request.app
        scope = request.scope
    else:
        app = websocket.app
        scope = websocket.scope

    yield ServiceFactory(
        repos,
        current_user=scope.get("user"),
        config=request.app.state.config,
        redis_client=app.state.redis,
    )
