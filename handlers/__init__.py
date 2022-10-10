from aiogram import Dispatcher, Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from misc.models.server import Server

from .group import create_group_router
from .public import create_public_router


def register_routers(dp: Dispatcher, server: Server, bot: Bot, scheduler: AsyncIOScheduler):
    dp.include_router(create_public_router(server, bot, scheduler))
    #dp.include_router(create_group_router())
