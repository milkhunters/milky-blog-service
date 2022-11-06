from fastapi import APIRouter

from config import load_config

import utils
from exceptions.models import ErrorAPIResponse

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
                "name": config.base.name,
                "mode": config.mode,
                "build": config.build,
                "build_date": config.build_date,
                "branch": config.branch,
                "commit_hash": config.commit_hash,
            }
        )
    return info


@router.get("/test")
async def test():
    return {
        "Redis": await utils.RedisClient.ping(),
    }
