from src.models.auth import UnauthenticatedUser
from src.models.permission import Permission


class PermissionApplicationService:

    async def guest_permissions(self) -> list[str]:
        return list(UnauthenticatedUser().permissions)

    async def app_permissions(self) -> list[str]:
        return [access.value for access in Permission]
