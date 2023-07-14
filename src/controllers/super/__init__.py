from fastapi import APIRouter

from . import moderator

router = APIRouter()

# router.include_router(moderator.router, dependencies=[Depends(RoleFilter(Role(M.moderator, A.one)))])
