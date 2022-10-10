from aiogram import Bot
from aiogram.types import Message

from misc.models.server import Server
from misc.utils import set_commands


async def command_start(message: Message, server: Server, bot: Bot):
    user = await server.send_message('user/get', {
        'tg_id': message.from_user.id
    })
    if not user:
        return await message.answer(text='Подключение к серверу отсутствует!')
    localization = await server.send_message(f'localization/{user.content.__data__.language_code}')

    await set_commands(bot, localization)
    await message.answer(text=localization.content.TID_START_TEXT % (
        user.content.__data__.nickname or message.from_user.first_name
    ))
