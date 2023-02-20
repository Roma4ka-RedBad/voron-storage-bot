from vkbottle.bot import MessageEvent

from bot_config import Config
from keyboards import commands_keyboard
from misc.custom_rules import PayloadRule
from misc.handler_utils import get_nickname

labeler = Config.labelers.new()
labeler.vbml_ignore_case = True


@labeler.raw_event(Config.callback, MessageEvent, PayloadRule({'command': 'start'}))
async def hello_callback_handler(event: MessageEvent, localization, userdata):
    keyboard = commands_keyboard(localization)
    await event.send_message(localization.START_VK_BODY.format(name=get_nickname(userdata)), keyboard=keyboard)


@labeler.raw_event(Config.callback, MessageEvent, PayloadRule({'type': 'show_snackbar'}))
async def show_snackbar_handler(event: MessageEvent, localization):
    await event.show_snackbar(localization[event.payload['TID']])
