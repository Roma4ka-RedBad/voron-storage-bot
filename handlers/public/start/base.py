from aiogram import Bot
from aiogram.types import Message

from misc.server import Server
from misc.utils import set_commands


async def command_start(message: Message, server: Server, bot: Bot):
    user = await server.send_message('user/get', {
        'tg_id': message.from_user.id
    })
    if not user:
        return await message.answer(text='Подключение к серверу отсутствует!')

    await set_commands(bot)
    await message.answer(
        text=f'Привет, {user.content.__data__.nickname or message.from_user.first_name}! Я помогу тебе с файлами бравл старса!'
    )
