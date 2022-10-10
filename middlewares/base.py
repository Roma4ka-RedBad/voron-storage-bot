from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class InitMiddleware(BaseMiddleware):
    def __init__(self, server, bot: Bot, scheduler: AsyncIOScheduler):
        self.server = server
        self.bot = bot
        self.scheduler = scheduler
        super().__init__()

    def create(self, data: Dict[str, Any]):
        data["bot"] = self.bot
        data["server"] = self.server
        data["scheduler"] = self.scheduler

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       obj: TelegramObject,
                       data: Dict[str, Any]):

        self.create(data)
        await handler(obj, data)
