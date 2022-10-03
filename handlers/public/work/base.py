from aiogram import Bot
from aiogram.types import Message

from misc.server import Server
from misc.utils import download_file, get_buttons


async def command_work(message: Message, server: Server, bot: Bot):
    config = await server.send_message('config')
    user = await server.send_message('user/get', {
        'tg_id': message.from_user.id
    })
    if not config:
        return await message.answer(text='Подключение к серверу отсутствует!')
    localization = await server.send_message(f'localization/{user.content.__data__.language_code}')

    if not message.document:
        return await message.answer(localization.content.TID_WORK_FILENOTEXIST % (
            user.content.__data__.nickname or message.from_user.first_name
        ))

    file = await download_file(message, bot, server, config.content.UFS.path)
    if not file:
        return await message.answer(localization.content.TID_WORK_DOWNLOADFALE % (
            user.content.__data__.nickname or message.from_user.first_name
        ))

    keyboard = await get_buttons(file, server)
    if not keyboard[0]:
        return await message.answer(localization.content[keyboard[1]] % (
            user.content.__data__.nickname or message.from_user.first_name
        ))

    return await message.answer(localization.content.TID_WORK_TEXT % (
        user.content.__data__.nickname or message.from_user.first_name
    ), reply_markup=keyboard[1])
