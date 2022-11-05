from vkbottle import GroupEventType
from vkbottle.bot import Blueprint, Message, MessageEvent
from pathlib import Path

from keyboard import compressed_photos_keyboard
from misc.custom_rules import PayloadRule
from misc.pathwork import download_files, remove_dir
from misc.connection.uploads import upload

bp = Blueprint('compressed photos convert commands')
bp.labeler.vbml_ignore_case = True


@bp.on.message(attachment='photo')
async def compressed_photo(message: Message, localization):
    await message.reply(
        localization.TID_COMPRESSED_PHOTOS_TEXT,
        keyboard=compressed_photos_keyboard(message.conversation_message_id))


@bp.on.raw_event(
    GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule(
        {'type': 'show_snackbar'}))
async def show_snackbar_handler(event: MessageEvent, localization):
    await event.show_snackbar(localization[event.payload['TID']])


@bp.on.raw_event(
    GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule(
        {'type': 'convert'}))
async def convert_photos(event: MessageEvent, user_api, bot, userdata, localization, payload, server, config):
    await event.edit_message(
        keep_forward_messages=True,
        keyboard='[]',
        message=localization.TID_STARTWORK)
    message = (await bp.api.messages.get_by_conversation_message_id(
        peer_id=event.peer_id,
        conversation_message_ids=payload.msg_id)).items[0]
    loaded_by_userapi = False
    photos = []

    for photo in message.attachments:
        photos.append(('photo', max(photo.photo.sizes, key=lambda x: (x.height, x.width))))

    files = await download_files(message, server, photos, config)
    done = []

    result = await server.send_message(
            f'convert/{payload.convert_to}',
            file=[{'path': file.get_dir()} for file in files],
            metadata={'compress_to_archive': False})

    if result.status:
        done, loaded_by_userapi = await upload([Path(file) for file in result.content.result],
                                               user_api, bot,
                                               localization, event.peer_id)

    user = (await bp.api.users.get(user_ids=[event.user_id]))[0]
    nickname = userdata.nickname or f'{user.first_name} {user.last_name}'
    if not done:
        text = localization.TID_STARTWORK_FILESNOTCONVERT.format(name=f'[id{user.id}|{nickname}]')
    elif len(done) < len(photos):
        text = localization.TID_SOME_FILES_CONVERTED.format(name=f'[id{user.id}|{nickname}]')
    elif len(done) == len(files):
        text = localization.TID_STARTWORK_DONE_FOR_MANY_FILES.format(name=f'[id{user.id}|{nickname}]')
    else:
        text = localization.TID_ERROR

    if loaded_by_userapi:
        await event.send_message(text, forward_messages=done)
    else:
        await event.send_message(text, attachment=done)
    await remove_dir(event.user_id, message.conversation_message_id, config)
