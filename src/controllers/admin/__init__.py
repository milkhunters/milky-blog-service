from fastapi import APIRouter, Depends

from dependencies import JWTCookie, RoleFilter
from models.role import Role
from models.role import MainRole as M
from models.role import AdditionalRole as A


from views import ErrorAPIResponse

from . import one

router = APIRouter(
    responses={"400": {"model": ErrorAPIResponse}},
    dependencies=[Depends(JWTCookie())]
)

router.include_router(one.router, dependencies=[Depends(RoleFilter(Role(M.moderator, A.one)))])
