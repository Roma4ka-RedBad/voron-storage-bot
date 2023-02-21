from vkbottle.bot import MessageEvent

from bot_config import Config
from keyboards import change_language_keyboard
from misc.connections import ServerConnection
from misc.custom_rules import PayloadRule
from misc.handler_utils import get_nickname
from misc.models import UserModel
from misc.packets import Packet

labeler = Config.labelers.new()
labeler.vbml_ignore_case = True


@labeler.raw_event(Config.callback, MessageEvent, PayloadRule({'command': 'change_language'}))
async def hello_callback_handler(event: MessageEvent, userdata: UserModel, server: ServerConnection, localization):
    user = (await Config.bot_api.users.get(user_ids=[event.user_id]))[0]
    lg_code = {'ru': 'en', 'en': 'ru'}[userdata.language_code]
    packet = await server.send(Packet(11101, vk_id=userdata.vk_id, set_key='language_code', set_value=lg_code))
    if not packet:
        await event.send_message(localization.UNKNOWN_ERROR)
        return

    localization = Config.localizations[lg_code]

    await event.edit_message(
            message=localization.PROFILE_BODY.format(
                    name=f'[id{user.id}|{user.first_name}]',
                    nickname=await get_nickname(userdata),
                    bot_id=userdata.id,
                    platform='VK',
                    platform_id=event.user_id,
                    rank=userdata.rank,
                    warnings=userdata.warns,
                    bind=userdata.tg_id or localization.MISSING_ERROR
            ),
            keyboard=change_language_keyboard(localization))
