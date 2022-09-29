from aiogram import Dispatcher, Bot
from misc.server import Server

from .group import create_group_router
from .public import create_public_router


def register_routers(dp: Dispatcher, server: Server, bot: Bot):
    dp.include_router(create_public_router(server, bot))
    #dp.include_router(create_group_router())
