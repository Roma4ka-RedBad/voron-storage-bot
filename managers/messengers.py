from typing import List
from loguru import logger
from logic_objects import Config, FileObject

from aiogram import Bot as TgBot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.types import InputMediaDocument, FSInputFile
from vkbottle.bot import Bot as VkBot


class MessengersManager:
    def __init__(self):
        self.tgbot = TgBot(token=Config.TG.token, parse_mode='HTML', session=AiohttpSession(
            api=TelegramAPIServer.from_base("http://localhost:8080", is_local=True)))
        logger.disable("vkbottle")
        self.vkbot = VkBot(Config.VK.bot_token)

    @staticmethod
    async def create_media_group(files: List[str] | List[FileObject]):
        media_group = []
        for file in files:
            media_group.append(InputMediaDocument(
                media=FSInputFile(file.path if isinstance(file, FileObject) else file)
            ))
        return media_group

    async def send_telegram_message(self, chat_ids: int | list, text: str, documents: List[InputMediaDocument] = None,
                                    **kwargs):
        if isinstance(chat_ids, int):
            chat_ids = [chat_ids]

        for chat_id in chat_ids:
            if documents:
                for document in documents:
                    if document == documents[-1]:
                        document.caption = text
                return await self.tgbot.send_media_group(chat_id, media=documents, **kwargs)
            return await self.tgbot.send_message(chat_id, text=text, **kwargs)

    async def send_vk_message(self):
        # Ну сделаю, как будет необходимость
        await self.vkbot.api.messages.send()
