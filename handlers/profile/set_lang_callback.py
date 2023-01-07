from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hcode, hbold

from packets.base import Packet
from misc.utils import FormString
from keyboards import set_commands
from keyboards.profile import ProfileCallback, profile_kb


async def profile_set_language(cbq: CallbackQuery, bot: Bot, server, callback_data: ProfileCallback, config_data):
    packet = await server.send(
        Packet(11101, tg_id=cbq.from_user.id, set_key="language_code", set_value=callback_data.language_code)
    )
    if packet:
        localization = config_data.localization[packet.payload.language_code]
        await cbq.answer(localization.PROCESS_DONE)

        if packet.payload.language_code == 'ru':
            packet.payload.language_code = 'en'
        else:
            packet.payload.language_code = 'ru'

        await cbq.message.edit_text(text=FormString.paste_args(localization.PROFILE_BODY,
            name=cbq.from_user.first_name,
            nickname=hbold(packet.payload.nickname or localization.MISSING_ERROR),
            bot_id=hcode(packet.payload.id),
            platform_id=hcode(cbq.from_user.id),
            rank=hbold(packet.payload.rank),
            warnings=hbold(packet.payload.warns),
            bind=hcode(packet.payload.vk_id or localization.MISSING_ERROR)
        ), reply_markup=profile_kb(packet.payload.language_code, localization))
        await set_commands(bot, localization, cbq.message.chat.id)
