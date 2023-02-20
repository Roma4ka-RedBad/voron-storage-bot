from vkbottle.bot import MessageEvent

from bot_config import Config
from misc.custom_rules import PayloadRule

labeler = Config.labelers.new()
labeler.vbml_ignore_case = True


@labeler.raw_event(Config.callback, MessageEvent, PayloadRule({'type': 'show_snackbar'}))
async def show_snackbar_handler(event: MessageEvent, localization):
    await event.show_snackbar(localization[event.payload['TID']])
