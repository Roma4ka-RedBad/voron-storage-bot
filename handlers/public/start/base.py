from aiogram import Bot
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from misc.utils import set_commands, check_server


async def command_start(message: Message, bot: Bot, user_data, user_localization):
    if not await check_server(message, user_localization):
        return

    await set_commands(bot, user_localization, message.chat.id)
    await message.answer(text=hbold(user_localization.TID_START_TEXT.format(
        name=user_data.nickname or message.from_user.first_name
    )))
