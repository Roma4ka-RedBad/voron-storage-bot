from aiogram.types import Message
from aiogram.utils.markdown import hcode, hbold

from misc.models import Server


async def command_markets(message: Message, server: Server, user_data, user_localization):
    if not user_localization:
        return await message.answer(text='Подключение к серверу отсутствует!')

    markets = (await server.send_msg(f'markets/{user_data.language_code}')).content
    print(markets)
    await message.answer_photo(markets['1'].artworkUrl512, caption=markets['1'].minimumOsVersion)
