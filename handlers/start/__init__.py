from aiogram import Bot
from aiogram.types import Message
from keyboards import set_commands
from misc.utils import FormString


async def command_start(message: Message, bot: Bot, user_data, localization):
    await set_commands(bot, localization, message.chat.id)
    await message.answer(text=FormString(localization.START_BODY).get_form_string(
        set_style="bold",
        name=user_data.nickname or message.from_user.full_name
    ))
