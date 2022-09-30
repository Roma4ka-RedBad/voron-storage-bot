from aiogram import Bot
from aiogram.types import Message

from misc.server import Server
from misc.utils import download_file, get_buttons


async def command_work(message: Message, server: Server, bot: Bot):
    config = await server.send_message('config')
    if not config:
        return await message.answer(text='Подключение к серверу отсутствует!')

    if not message.document:
        return await message.answer(text='Для работы команды нужно прикрепить файл!')

    file = await download_file(message, bot, server, config.content.UFS.path)
    if not file:
        return await message.answer(text='Не удалось скачать файл! Возможно он слишком много весит...')

    keyboard = await get_buttons(file, server)
    if not keyboard[0]:
        return await message.answer(text=keyboard[1])

    await message.answer(text=f'{message.from_user.first_name}, выбери нужную команду для этого файла:',
                         reply_markup=keyboard[1])
