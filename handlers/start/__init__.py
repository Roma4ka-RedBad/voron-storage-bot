from aiogram import Bot
from aiogram.types import Message
from keyboards import set_commands
from misc.utils import easy_format


async def command_start(message: Message, bot: Bot, user_data, localization):
    await set_commands(bot, localization, message.chat.id)
    await message.answer(text=easy_format(localization.START_BODY, formatting=["bold"],
                                          name=user_data.nickname or message.from_user.full_name))
