from aiogram.types import Message
from aiogram.utils.markdown import hcode, hbold

from misc.models.server import Server


async def command_profile(message: Message, server: Server):
    user = await server.send_message('user/get', {
        'tg_id': message.from_user.id
    })
    if not user:
        return await message.answer(text='Подключение к серверу отсутствует!')
    localization = await server.send_message(f'localization/{user.content.__data__.language_code}')

    await message.answer(text=localization.content.TID_PROFILE_TEXT % (
        message.from_user.first_name,
        hbold(user.content.__data__.nickname or 'ОТСУТСТВУЕТ'),
        hcode(user.content.__data__.id),
        server.messenger, hcode(message.from_user.id),
        hbold(user.content.__data__.rank),
        hbold(user.content.__data__.warns),
        hcode(user.content.__data__.vk_id or 'ОТСУТСТВУЕТ')
    ))
