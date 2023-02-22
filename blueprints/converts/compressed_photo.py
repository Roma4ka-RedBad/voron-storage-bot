from pathlib import Path

from vkbottle.bot import Message, MessageEvent

from bot_config import Config
from keyboards import compressed_photos_keyboard
from misc.connections import ServerConnection
from misc.connections.uploads import upload
from misc.custom_rules import PayloadRule
from misc.handler_utils import get_nickname
from misc.packets import Packet
from misc.pathwork import download_and_register_files

labeler = Config.labelers.new()
labeler.vbml_ignore_case = True


@labeler.message(attachment='photo')
async def compressed_photo(message: Message, localization):
    await message.reply(message=localization.WORK_COMPRESSED_PHOTOS,
                        keyboard=compressed_photos_keyboard(message.conversation_message_id))


@labeler.raw_event(Config.callback, MessageEvent, PayloadRule({'type': 'convert'}))
async def convert_photos(event: MessageEvent, server: ServerConnection, localization, payload, userdata):
    await event.edit_message(keep_forward_messages=True,
                             keyboard='[]',
                             message=localization.WORK_START)

    photos = []
    message = (await Config.bot_api.messages.
               get_by_conversation_message_id(peer_id=event.peer_id, conversation_message_ids=payload.msg_id)
               ).items[0]
    nickname = await get_nickname(userdata)
    for photo in message.attachments:
        photos.append(('photo', max(photo.photo.sizes, key=lambda x: (x.height, x.width))))

    object_id = await download_and_register_files(photos, server, userdata, localization, message)
    if object_id is None:
        return

    converted = await server.send(Packet(13104, object_id=object_id, convert_method=payload.convert_to))
    if converted:
        if converted.payload.get('error_tid'):
            await event.send_message(localization[converted.payload.error_tid].format(name=nickname))
            return

    done, loaded_by_userapi = await upload([Path(file) for file in converted.payload.result],
                                           localization, event.peer_id)

    if len(done) < len(photos) and not loaded_by_userapi:
        text = localization.WORK_SOME_FILES_CONVERTED_ERROR.format(name=nickname)
    elif len(done) == len(photos) and not loaded_by_userapi:
        text = localization.WORK_DONE_FOR_MANY_FILES.format(name=nickname)
    elif loaded_by_userapi:
        text = localization.WORK_DONE.format(name=nickname)
    else:
        text = localization.UNKNOWN_ERROR

    if loaded_by_userapi:
        await event.send_message(text, forward=done)
    else:
        await event.send_message(text, attachment=done)
