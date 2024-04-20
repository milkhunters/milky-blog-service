from fastapi.requests import Request
from fastapi.websockets import WebSocket

from mbs.services.repository import RepoFactory


async def get_repos(request: Request = None, websocket: WebSocket = None) -> RepoFactory:
    if request:
        app = request.app
    else:
        app = websocket.app
    async with app.state.db_session() as session:
        yield RepoFactory(session)
