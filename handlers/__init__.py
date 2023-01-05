from aiogram import Router, Bot
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from packets.base import Packet

from .start import command_start
from .set_name import command_setname
from .actions_msg import command_sendmsg, command_editmsg


class Middleware(BaseMiddleware):
    def __init__(self, bot: Bot, server):
        self.bot = bot
        self.server = server
        super().__init__()

    def client_data(self, data: Dict[str, Any]):
        data["bot"] = self.bot
        data["server"] = self.server

    async def server_data(self, data: Dict[str, Any], obj: TelegramObject):
        message = obj if isinstance(obj, Message) else obj.message if isinstance(obj, CallbackQuery) else None
        if message:
            config_data = self.server.events_handler.get_config_data()
            if await self.server.is_connected():
                data["user_data"] = await self.server.send(Packet(11100, tg_id=message.from_user.id))
                data["user_data"] = data["user_data"].payload
                data["localization"] = config_data.localization[data["user_data"].language_code]
                return True
            else:
                language_code = "ru" if message.from_user.language_code == "ru" else "en"
                await message.answer(config_data.localization[language_code].TID_NO_CONNECTION)

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], obj: TelegramObject,
                       data: Dict[str, Any]):
        self.client_data(data)
        if await self.server_data(data, obj):
            await handler(obj, data)


def create_public_router(bot: Bot, server) -> Router:
    public_router: Router = Router(name="public_router")

    public_router.message.middleware(Middleware(bot, server))
    public_router.message.register(command_start, commands=["start"])
    public_router.message.register(command_sendmsg, commands=["send"])
    public_router.message.register(command_editmsg, commands=["down"])
    public_router.message.register(command_setname, commands=["name"])

    return public_router
