from aiogram import Dispatcher, Bot
from misc.models import Server, Scheduler, FilesStorage

from .group import create_group_router
from .public import create_public_router


def register_routers(dp: Dispatcher, server: Server, bot: Bot, scheduler: Scheduler, fstorage: FilesStorage):
    dp.include_router(create_public_router(server, bot, scheduler, fstorage))
    #dp.include_router(create_group_router())
