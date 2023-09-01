from src.models.auth import UnauthenticatedUser
from src.models.access import AccessTags


class RoleApplicationService:

    async def guest_access(self) -> list[str]:
        return list(UnauthenticatedUser().access)

    async def app_access(self) -> list[str]:
        return [access.value for access in AccessTags]