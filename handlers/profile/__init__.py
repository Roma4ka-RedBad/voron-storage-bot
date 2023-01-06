from aiogram.types import Message
from aiogram.utils.markdown import hcode, hbold
from misc.utils import easy_format
from keyboards.profile import profile_kb


async def command_profile(message: Message, user_data, localization):
    if user_data.language_code == 'ru':
        user_data.language_code = 'en'
    else:
        user_data.language_code = 'ru'

    await message.answer(text=easy_format(localization.PROFILE_BODY,
        name=message.from_user.first_name,
        nickname=hbold(user_data.nickname or localization.MISSING_ERROR),
        bot_id=hcode(user_data.id),
        platform_id=hcode(message.from_user.id),
        rank=hbold(user_data.rank),
        warnings=hbold(user_data.warns),
        bind=hcode(user_data.vk_id or localization.MISSING_ERROR)
    ), reply_markup=profile_kb(user_data.language_code, localization))
