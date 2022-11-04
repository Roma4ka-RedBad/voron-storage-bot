from vkbottle import GroupEventType, DocMessagesUploader
from vkbottle.bot import Blueprint, Message, MessageEvent

from keyboard import audio_keyboard
from misc.custom_rules import PayloadRule
from misc.pathwork import download_files, remove_dir

from box import Box

bp = Blueprint('only audio convert commands')


@bp.on.message(attachment='audio')
async def audio_handler(message: Message, localization):
    await message.reply(
        localization.TID_CHOOSE_AUDIO_CONVERT,
        keyboard=audio_keyboard(message.conversation_message_id, localization))


@bp.on.raw_event(
    GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule(
        {'type': 'audio_convert'}))
async def audio_convert_handler(event: MessageEvent, localization, server, config, userdata,
                                payload):
    message = (await bp.api.messages.get_by_conversation_message_id(
        peer_id=event.peer_id,
        conversation_message_ids=payload.msg_id)).items[0]
    user = (await bp.api.users.get(user_ids=[event.user_id]))[0]
    nickname = userdata.nickname or f'{user.first_name} {user.last_name}'

    await event.edit_message(
        keep_forward_messages=True,
        keyboard='[]',
        message=localization.TID_STARTWORK.format(name=f'[id{user.id}|{nickname}]'))

    audios = [('audio', i.audio) for i in message.attachments]
    files = await download_files(message, server, audios, config)
    done = []

    warning_tid = ''
    if not files:
        await event.send_message(localization.TID_WORK_DOWNLOAD_AUDIOS_FAILED.format(name=f'[id{user.id}|{nickname}]'))
        return
    elif len(files) < len(audios):
        warning_tid = localization.TID_WORK_DOWNLOAD_SOME_AUDIOS_FAILED.format(name=f'[id{user.id}|{nickname}]')

    result = await server.send_message(
        f'convert/{payload.convert_to}',
        file=[{'path': file.get_dir()} for file in files],
        metadata={
            'compress_to_archive': True,
            'archive_only': True,
            'compress': payload.compress
            })
    if result.status:
        response_file = result.content.result
        print(response_file)
        loaded = await DocMessagesUploader(bp.api).upload(
            'result.zip1',
            open(response_file, 'rb').read(),
            peer_id=event.peer_id)
        done.append(loaded)

    if not done:
        text = warning_tid + '\n' + \
               localization.TID_STARTWORK_FILESNOTCONVERT.format(name=f'[id{user.id}|{nickname}]')
    elif len(done) == 1:
        text = warning_tid + '\n' + \
               localization.TID_ARCHIVEISRENAMED.format(name=f'[id{user.id}|{nickname}]')
    else:
        text = localization.TID_ERROR

    await event.send_message(text, attachment=done)
