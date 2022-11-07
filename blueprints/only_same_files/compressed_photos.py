from vkbottle import GroupEventType, API
from vkbottle.bot import Blueprint, Message, MessageEvent
from pathlib import Path

from keyboard import compressed_photos_keyboard
from misc.custom_rules import PayloadRule
from misc.pathwork import download_files
from misc.connection.uploads import upload
from misc.tools import remove_dir_and_file
from misc.models import Server, FileStorage, Scheduler

bp = Blueprint('compressed photos convert commands')


@bp.on.message(attachment='photo')
async def compressed_photo(message: Message, localization):
    await message.reply(message=localization.TID_COMPRESSED_PHOTOS_TEXT,
                        keyboard=compressed_photos_keyboard(message.conversation_message_id))


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'type': 'convert'}))
async def convert_photos(event: MessageEvent, user_api: API, file_storage: FileStorage, scheduler: Scheduler,
                         server: Server, localization, payload,  userdata, config):
    await event.edit_message(keep_forward_messages=True,
                             keyboard='[]',
                             message=localization.TID_STARTWORK)

    loaded_by_userapi = False
    done = []
    photos = []
    message = (await bp.api.messages.
               get_by_conversation_message_id(peer_id=event.peer_id, conversation_message_ids=payload.msg_id)
               ).items[0]
    user = (await bp.api.users.get(user_ids=[event.user_id]))[0]
    nickname = userdata.nickname or f'{user.first_name} {user.last_name}'
    for photo in message.attachments:
        photos.append(('photo', max(photo.photo.sizes, key=lambda x: (x.height, x.width))))
    files = await download_files(message, server, photos, scheduler, file_storage, config)
    result = await server.send_message(endpoint=f'convert/{payload.convert_to}',
                                       file=[{'path': file.get_dir()} for file in files],
                                       metadata={'compress_to_archive': False})

    if result.status:
        done, loaded_by_userapi = await upload([Path(file.path) for file in result.content.result if file.path],
                                               user_api, bp, localization, event.peer_id)

    if not done:
        text = localization.TID_STARTWORK_FILESNOTCONVERT.format(name=f'[id{user.id}|{nickname}]')
    elif len(done) < len(photos) and not loaded_by_userapi:
        text = localization.TID_SOME_FILES_CONVERTED.format(name=f'[id{user.id}|{nickname}]')
    elif len(done) == len(files) and not loaded_by_userapi:
        text = localization.TID_STARTWORK_DONE_FOR_MANY_FILES.format(name=f'[id{user.id}|{nickname}]')
    elif loaded_by_userapi:
        text = localization.TID_STARTWORK_DONE.format(name=f'[id{user.id}|{nickname}]')
    else:
        text = localization.TID_ERROR

    if loaded_by_userapi:
        await event.send_message(text, forward=done)
    else:
        await event.send_message(text, attachment=done)

    remove_dir_and_file(file_storage, payload.msg_id, event.user_id, config)
