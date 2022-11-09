from aiogram import Bot
from aiogram.types import Message

from misc.utils import set_commands


async def command_start(message: Message, bot: Bot, user_data, user_localization):
    if not user_data:
        return await message.answer(text='Подключение к серверу отсутствует!')

    await set_commands(bot, user_localization, message.chat.id)
    await message.answer(text=user_localization.TID_START_TEXT.format(
        name=user_data.nickname or message.from_user.first_name
    ))
