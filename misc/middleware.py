from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from packets.base import Packet


class Middleware(BaseMiddleware):
    def __init__(self, bot: Bot, server):
        self.bot = bot
        self.server = server
        super().__init__()

    async def client_data(self, data: Dict[str, Any]):
        data["bot"] = self.bot
        data["server"] = self.server

    async def server_data(self, data: Dict[str, Any], obj: TelegramObject):
        message = obj if isinstance(obj, Message) else obj.message if isinstance(obj, CallbackQuery) else None
        if message:
            data["config_data"] = self.server.events_handler.config_data
            if user_data := await self.server.send(Packet(11100, tg_id=message.from_user.id)):
                data["user_data"] = user_data.payload
                data["localization"] = data["config_data"].localization[user_data.payload.language_code]
                return True
            else:
                language_code = "ru" if message.from_user.language_code == "ru" else "en"
                await message.answer(data["config_data"].localization[language_code].NO_CONNECTION_ERROR)

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], obj: TelegramObject,
                       data: Dict[str, Any]):
        await self.client_data(data)
        if await self.server_data(data, obj):
            await handler(obj, data)
