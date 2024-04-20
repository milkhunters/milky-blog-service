from fastapi import Depends
from fastapi.requests import Request

from src import get_repos
from mbs.services import ServiceFactory
from mbs.services.repository import RepoFactory


async def get_services(
        request: Request,
        repos: RepoFactory = Depends(get_repos)
) -> ServiceFactory:
    global_scope = request.app.state
    local_scope = request.scope

    yield ServiceFactory(
        repos,
        current_user=local_scope.get("user"),
        config=global_scope.config,
        file_storage=global_scope.file_storage,
    )
