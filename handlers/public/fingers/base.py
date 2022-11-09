from aiogram.types import Message
from aiogram.utils.markdown import hcode, hbold

from misc.models import Server


async def command_fingers(message: Message, server: Server, user_data, user_localization):
    if not user_data:
        return await message.answer(text='Подключение к серверу отсутствует!')

    fingers = await server.send_msg('fingerprints')
    print(fingers)

    await message.answer(text=user_localization.TID_PROFILE_TEXT)
