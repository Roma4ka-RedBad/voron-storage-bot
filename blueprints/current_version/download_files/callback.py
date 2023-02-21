from bot_config import Config
from misc.connections import ServerConnection
from misc.models import UserModel
from misc.packets import Packet
from pathlib import Path

from vkbottle.bot import MessageEvent

from keyboards import archive_with_all_files_keyboard
from misc.connections.uploads import upload, get_valid_link
from misc.custom_rules import PayloadRule
from misc.handler_utils import get_nickname

labeler = Config.labelers.new()
labeler.vbml_ignore_case = True


@labeler.raw_event(Config.callback, MessageEvent, PayloadRule({'command': 'remove_paths'}))
async def remove_paths_callback_handler(event: MessageEvent, localization):
    msg = await Config.bot_api.messages.get_by_conversation_message_id(
            peer_id=event.peer_id,
            conversation_message_ids=[event.conversation_message_id])

    attachments = None
    if msg.items[0].attachments:
        attachments = [get_valid_link(item) for item in msg.items[0].attachments]

    await event.edit_message(
            message='\n'.join([row.split('/')[-1] for row in msg.items[0].text.split('\n')]),
            keyboard=archive_with_all_files_keyboard(localization, event.conversation_message_id),
            attachment=attachments)
    await event.show_snackbar(localization.PROCESS_DONE)


@labeler.raw_event(Config.callback, MessageEvent, PayloadRule({'command': 'download_all_files'}))
async def get_all_files_callback_handler(event: MessageEvent, userdata: UserModel, server: ServerConnection,
                                         payload, localization):
    msg_id = (await event.send_message(localization.DOWNLOADFILES_START.format(
            total_files_count=0,
            max_files_count=payload.count))).conversation_message_id
    packet = await server.send(
            Packet(13103,
                   object_id=payload.obj_id,
                   message_id=msg_id,
                   language_code=userdata.language_code,
                   compress_to_archive=payload.has_music or payload.many_files,
                   divider=1))
    await Config.bot_api.messages.edit(message=localization.DOWNLOADFILES_UPLOAD,
                                       peer_id=event.peer_id, conversation_message_id=msg_id)

    if packet:
        if packet.payload.get("error_tid", None):
            return await event.send_message(localization[packet.payload.error_tid])
        answer = localization.WORK_DONE_FOR_MANY_FILES.format(name=get_nickname(userdata))

        if isinstance(packet.payload.result, list):
            result = [Path(i) for i in packet.payload.result]
        else:
            if payload.has_music:
                answer = localization.WORK_ARCHIVE_IS_RENAMED
            result = [Path(packet.payload.result)]

        result, loaded_by_user = await upload(result, localization, event.user_id, payload.compress)

        if loaded_by_user:
            await event.send_message(answer, forward=result, keyboard='[]')
        else:
            await event.send_message(answer, attachment=result, keyboard='[]')

    else:
        await event.send_message(localization.UNKNOWN_ERROR)

    await Config.bot_api.messages.delete(delete_for_all=True, peer_id=event.peer_id, cmids=msg_id)
