from aiogram.types import Message
from aiogram.utils.markdown import hcode, hbold

from misc.models import Server
from misc.utils import check_server
from keyboards.profile import profile_kb


async def command_profile(message: Message, server: Server, user_data, user_localization):
    if not await check_server(message, user_localization):
        return

    if user_data.language_code == 'ru':
        user_data.language_code = 'en'
    else:
        user_data.language_code = 'ru'

    await message.answer(text=user_localization.TID_PROFILE_TEXT.format(
        name=message.from_user.first_name,
        nickname=hbold(user_data.nickname or user_localization.TID_FAIL),
        bot_id=hcode(user_data.id),
        platform=server.messenger,
        platform_id=hcode(message.from_user.id),
        rank=hbold(user_data.rank),
        warnings=hbold(user_data.warns),
        bind=hcode(user_data.vk_id or user_localization.TID_FAIL)
    ), reply_markup=profile_kb(user_data.language_code, user_localization))
