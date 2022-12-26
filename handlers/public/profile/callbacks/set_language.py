from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hcode, hbold

from misc.models import Server
from misc.utils import set_commands, check_server
from keyboards.profile import ProfileCallback, profile_kb


async def profile_set_language(cbq: CallbackQuery, bot: Bot, server: Server, callback_data: ProfileCallback):
    user_data = await server.send_msg('user/set', tg_id=cbq.from_user.id, set_key='language_code',
                                 set_value=callback_data.language_code)
    if not await check_server(cbq.message, user_data):
        return

    user_data = user_data.content
    user_localization = (await server.send_msg(f'user/localization/{callback_data.language_code}')).content

    if user_data.language_code == 'ru':
        user_data.language_code = 'en'
    else:
        user_data.language_code = 'ru'

    await cbq.message.edit_text(text=user_localization.TID_PROFILE_TEXT.format(
        name=cbq.from_user.first_name,
        nickname=hbold(user_data.nickname or user_localization.TID_FAIL),
        bot_id=hcode(user_data.id),
        platform=server.messenger,
        platform_id=hcode(cbq.from_user.id),
        rank=hbold(user_data.rank),
        warnings=hbold(user_data.warns),
        bind=hcode(user_data.vk_id or user_localization.TID_FAIL)
    ), reply_markup=profile_kb(user_data.language_code, user_localization))

    await set_commands(bot, user_localization, cbq.message.chat.id)

    await cbq.answer(user_localization.TID_DONE)
