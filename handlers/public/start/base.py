from aiogram.types import Message

from keyboards.start import start_kb
from misc.server import Server


async def command_start(message: Message, server: Server):
    config = await server.send_message('config')
    if not config:
        return await message.answer(text='Подключение к серверу отсутствует!')

    await message.answer(text=f'Привет, {message.from_user.full_name}! Лимиты: {str(config.content.FILE_SIZE_LIMITS)}',
                         reply_markup=start_kb())
