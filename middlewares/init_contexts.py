from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, Bot
from aiohttp import ClientSession
from aiogram.types import TelegramObject


class InitMiddleware(BaseMiddleware):
    def __init__(self, server, bot: Bot):
        self.server = server
        self.bot = bot
        super().__init__()

    def create_contexts(self, data: Dict[str, Any]):
        data["bot"] = self.bot
        data["server"] = self.server

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       obj: TelegramObject,
                       data: Dict[str, Any]):

        self.create_contexts(data)
        await handler(obj, data)
