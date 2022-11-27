from misc import utils
from fastapi import APIRouter
from logic_objects import Config

about_router = APIRouter()


@about_router.get("/config")
async def get_config():
    return await utils.create_response(True, content=Config)
