from vkbottle import GroupEventType, API
from vkbottle.bot import Blueprint, Message, MessageEvent
from pathlib import Path

from keyboard import converts_keyboard
from misc.custom_rules import PayloadRule
from misc.pathwork import download_files
from misc.connection.uploads import upload
from misc.models import FileStorage, Server, Scheduler
from misc.tools import remove_dir_and_file

bp = Blueprint('all documents convert commands')


@bp.on.private_message(attachment=['doc', 'photo', 'video', 'audio', 'wall', 'market'])
async def documents_handler(message: Message, server: Server, file_storage: FileStorage, scheduler: Scheduler,
                            config, localization, userdata):
    files = []
    for file in message.attachments:
        if file.audio:
            files.append(('audio', file.audio))
        elif file.doc:
            files.append(('doc', file.doc))
        elif file.video:
            pass

    if not files:
        return

    files = await download_files(message, server, files, scheduler, file_storage, localization, config)
    if files is None:
        return

    user = (await bp.api.users.get(user_ids=[message.from_id]))[0]
    nickname = userdata.nickname or f'{user.first_name} {user.last_name}'

    response = await server.send_message(f'converts', [{'path': str(file.get_dir())} for file in files])
    if not response.status:
        if isinstance(response.error_msg, str):
            await message.reply(localization[response.error_msg].format(name=nickname))
        else:
            await message.reply(
                localization[response.error_msg.tid].format(count=response.error_msg.files_count,
                                                            maximum=response.error_msg.maximum))
        return

    file_storage.put(message.from_id, message.conversation_message_id, response.content)
    buttons = file_storage.get_converts(message.from_id, message.conversation_message_id)
    keyboard = converts_keyboard(buttons, localization, message.conversation_message_id)

    if not keyboard:
        await message.reply(localization.TID_WORK_FORMATSNOTEXIST.format(name=nickname))
    else:
        await message.reply(localization.TID_WORK_TEXT.format(name=nickname), keyboard=keyboard)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'type': 'doc_convert'}))
async def convert_documents_handler(event: MessageEvent, user_api: API, server: Server, file_storage: FileStorage,
                                    userdata, localization, payload, config, scheduler):
    await event.edit_message(keep_forward_messages=True,
                             keyboard='[]',
                             message=localization.TID_STARTWORK)

    prepared = []
    files = file_storage.get_files(event.user_id, payload.msg_id)

    for file in files:
        if payload.convert_to in files[file]:
            prepared.append({'path': file})

    if not files:
        await event.send_message(localization.TID_STARTWORK_FILENOTFOUND)
        return

    scheduler.pause_task(task_id=(event.user_id, payload.msg_id)).on(2).minutes()
    result = await server.send_message(endpoint=f'convert/{payload.convert_to}',
                                       file=prepared,
                                       metadata={'compress_to_archive': True,
                                                 'archive_only': True})

    user = (await bp.api.users.get(user_ids=[event.user_id]))[0]
    nickname = userdata.nickname or f'{user.first_name} {user.last_name}'
    if result.status:
        done, loaded_by_userapi = await upload([Path(result.content.result)], user_api, bp, localization,
                                               event.peer_id, payload.convert_to in ['mp3', 'ogg', 'waw'])

        text = localization.TID_STARTWORK_DONE.format(name=f'[id{user.id}|{nickname}]')

        if loaded_by_userapi:
            await event.send_message(text, forward=done)
        else:
            await event.send_message(text, attachment=done)
    else:
        await event.send_message(localization[result.error_msg])

    await remove_dir_and_file(file_storage, payload.msg_id, event.user_id, config)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'type': 'move_page'}))
async def switch_page_handler(event: MessageEvent, file_storage: FileStorage, userdata, localization, payload):
    buttons = file_storage.get_converts(event.user_id, payload.msg_id)
    keyboard = converts_keyboard(buttons, localization, payload.msg_id, page=payload.page)

    if not keyboard:
        await event.edit_message(localization.TID_STARTWORK_FILENOTFOUND)
    else:
        user = (await bp.api.users.get(user_ids=[event.user_id]))[0]
        nickname = userdata.nickname or f'{user.first_name} {user.last_name}'
        await event.edit_message(message=localization.TID_WORK_TEXT.format(name=nickname),
                                 keyboard=keyboard,
                                 keep_forward_messages=True)
