from vkbottle import GroupEventType
from vkbottle.bot import Blueprint, Message, MessageEvent
from pathlib import Path

from keyboard import audio_keyboard
from misc.custom_rules import PayloadRule
from misc.pathwork import download_files
from misc.connection.uploads import upload
from misc.tools import remove_dir_and_file
from misc.models import FileStorage, Scheduler, Server

bp = Blueprint('only audio convert commands')


@bp.on.message(attachment='audio')
async def audio_handler(message: Message, localization, userdata):
    user = (await bp.api.users.get(user_ids=[message.from_id]))[0]
    nickname = userdata.nickname or f'{user.first_name} {user.last_name}'

    await message.reply(
        message=localization.TID_CHOOSE_AUDIO_CONVERT.format(name=nickname),
        keyboard=audio_keyboard(message.conversation_message_id, localization))


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'type': 'audio_convert'}))
async def audio_convert_handler(event: MessageEvent, file_storage: FileStorage, scheduler: Scheduler,
                                server: Server, localization, config, userdata, payload, user_api):
    await event.edit_message(keep_forward_messages=True,
                             keyboard='[]',
                             message=localization.TID_STARTWORK)

    loaded_by_userapi = False
    done = []
    warning_tid = ''
    message = (await bp.api.messages
               .get_by_conversation_message_id(peer_id=event.peer_id, conversation_message_ids=payload.msg_id)
               ).items[0]
    user = (await bp.api.users.get(user_ids=[event.user_id]))[0]
    nickname = userdata.nickname or f'{user.first_name} {user.last_name}'
    audios = [('audio', i.audio) for i in message.attachments]
    files = await download_files(message, server, audios, scheduler, file_storage, config)

    if not files:
        await event.send_message(localization.TID_WORK_DOWNLOAD_AUDIOS_FAILED.format(name=f'[id{user.id}|{nickname}]'))
        return

    elif len(files) < len(audios):
        warning_tid = localization.TID_WORK_DOWNLOAD_SOME_AUDIOS_FAILED.format(name=f'[id{user.id}|{nickname}]')

    result = await server.send_message(endpoint=f'convert/{payload.convert_to}',
                                       file=[{'path': file.get_dir()} for file in files],
                                       metadata={'compress_to_archive': True,
                                                 'archive_only': True,
                                                 'compress': payload.compress})
    if result.status:
        done, loaded_by_userapi = await upload([Path(result.content.result)], user_api, bp, localization,
                                               event.peer_id, rename=True)

    if not done:
        text = warning_tid + '\n' + localization.TID_STARTWORK_FILESNOTCONVERT.format(name=f'[id{user.id}|{nickname}]')
    else:
        text = warning_tid + '\n' + localization.TID_ARCHIVEISRENAMED.format(name=f'[id{user.id}|{nickname}]')

    if loaded_by_userapi:
        await event.send_message(text, forward=done)
    else:
        await event.send_message(text, attachment=done)

    await remove_dir_and_file(file_storage, payload.msg_id, event.user_id, config)
