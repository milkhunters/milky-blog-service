from fastapi import APIRouter

from src.config import load_config

import utils
from views import ErrorAPIResponse

router = APIRouter(responses={"400": {"model": ErrorAPIResponse}})
config = load_config()


@router.get("/version")
async def version(details: bool = False):
    info = {
        "version": config.base.vers,
    }
    if details:
        info.update(
            {
                "name": None,
                "mode": config.mode,
                "build": None,
                "build_date": None,
                "branch": None,
                "commit_hash": None,
            }
        )
    return info


@router.get("/test")
async def test():
    return {
        "Redis": await utils.RedisClient.ping(),
    }
