from aiogram.types import Message

from keyboards.start import start_kb
from misc.server import Server


async def command_start(message: Message, server: Server):
    config = await server.send_message('config')
    await message.answer(text=f'Привет, {message.from_user.full_name}! Лимиты: {str(config.FILE_SIZE_LIMITS)}',
                         reply_markup=start_kb())
