from aiogram.types import Message
from aiogram.utils.markdown import hcode, hbold

from misc.server import Server


async def command_profile(message: Message, server: Server):
    user = await server.send_message('user/get', {
        'tg_id': message.from_user.id
    })
    if not user:
        return await message.answer(text='Подключение к серверу отсутствует!')

    await message.answer(text=f"{message.from_user.first_name}, ваш профиль: "
                              f"\n  НИК: {hbold(user.content.__data__.nickname or message.from_user.full_name)}"
                              f"\n  ID: {hcode(user.content.__data__.id)}"
                              f"\n  {server.messenger}_ID: {hcode(message.from_user.id)}"
                              f"\n  РАНГ: {hbold(user.content.__data__.rank)}"
                              f"\n  ПРЕДУПРЕЖДЕНИЯ: {hbold(user.content.__data__.warns)}"
                              f"\n  ПРИВЯЗКА: {hcode(user.content.__data__.vk_id or 'ОТСУТСТВУЕТ')}")
