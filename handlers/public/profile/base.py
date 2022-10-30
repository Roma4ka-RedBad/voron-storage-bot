from aiogram.types import Message
from aiogram.utils.markdown import hcode, hbold

from misc.models import Server


async def command_profile(message: Message, server: Server, user_data, user_localization):
    if not user_data:
        return await message.answer(text='Подключение к серверу отсутствует!')

    await message.answer(text=user_localization.TID_PROFILE_TEXT.format(
        name=message.from_user.first_name,
        nickname=hbold(user_data.nickname or user_localization.TID_FAIL),
        bot_id=hcode(user_data.id),
        platform=server.messenger,
        platform_id=hcode(message.from_user.id),
        rank=hbold(user_data.rank),
        warnings=hbold(user_data.warns),
        bind=hcode(user_data.vk_id or user_localization.TID_FAIL)
    ))
