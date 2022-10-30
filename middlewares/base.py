from typing import Callable, Dict, Any, Awaitable

from misc.models import Server, Scheduler, FilesStorage

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject


class Middleware(BaseMiddleware):
    def __init__(self, server: Server, bot: Bot, scheduler: Scheduler, fstorage: FilesStorage):
        self.server = server
        self.bot = bot
        self.scheduler = scheduler
        self.fstorage = fstorage
        super().__init__()

    def client_data(self, data: Dict[str, Any]):
        data["bot"] = self.bot
        data["server"] = self.server
        data["scheduler"] = self.scheduler
        data["fstorage"] = self.fstorage

    async def server_data(self, data: Dict[str, Any], obj: TelegramObject):
        data['server_config'] = None
        data['user_data'] = None
        data['user_localization'] = None

        if config := await data['server'].send_msg('config'):
            data['server_config'] = config.content

        if from_user := getattr(obj, 'from_user'):
            if user := await data['server'].send_msg('user/get', tg_id=from_user.id):
                data['user_data'] = user.content.__data__
                data['user_localization'] = (
                    await data['server'].send_msg(f'localization/{data["user_data"].language_code}')
                ).content

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       obj: TelegramObject,
                       data: Dict[str, Any]):
        self.client_data(data)
        await self.server_data(data, obj)
        await handler(obj, data)
