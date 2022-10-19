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

    def init_data(self, data: Dict[str, Any]):
        data["bot"] = self.bot
        data["server"] = self.server
        data["scheduler"] = self.scheduler

    async def user_data(self, data: Dict[str, Any], obj: TelegramObject):
        data['server_config'] = None
        data['user_data'] = None
        data['user_localization'] = None

        if config := await data['server'].send_message('config'):
            data['server_config'] = config.content

        if from_user := getattr(obj, 'from_user'):
            if user := await data['server'].send_message('user/get', {'tg_id': from_user.id}):
                data['user_data'] = user.content.__data__
                data['user_localization'] = (
                    await data['server'].send_message(f'localization/{data["user_data"].language_code}')
                ).content

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       obj: TelegramObject,
                       data: Dict[str, Any]):
        self.init_data(data)
        await self.user_data(data, obj)
        await handler(obj, data)
