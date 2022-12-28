from pathlib import Path

from vkbottle import GroupEventType
from vkbottle.bot import Message, MessageEvent

from config import bot_config
from keyboard import server_downloads_keyboard, archive_with_all_files_keyboard
from misc.connection.uploads import upload, get_valid_link
from misc.custom_rules import StartFromRule, PayloadRule
from misc.handler_utils import get_nickname, Regex, commands_to_regex
from misc.models import Server, Scheduler
from misc.tools import remove_dir_and_file
from misc.models import FileStorage

labeler = bot_config.labelers.new()
labeler.vbml_ignore_case = True


@labeler.message(regexp=commands_to_regex('скачать файл', 'download file', 'download', 'скачать', exactly=True))
@labeler.private_message(text=('скачать файл', 'download file', 'download', 'скачать'))
async def download_file_without_args_handler(message, localization, userdata):
    await message.answer(
            localization.TID_DOWNLOAD_FILES_WITHOUT_ARGS.format(name=await get_nickname(userdata, bot_config.api))
    )


@labeler.message(StartFromRule(regex_pattern=commands_to_regex(
        'скачать файл', 'download file', 'download', 'скачать', 'get', 'download')))
async def download_file_handler(message: Message, localization, server: Server, userdata, user_api,
                                scheduler: Scheduler, file_storage: FileStorage, config):
    raw_text = Regex(message.text).split(',| |\n')
    version = Regex(' '.join(raw_text)).search(r"\d+[\.]\d+([\.]\d+)?")
    version = version[0] if version else None
    major_v, build_v, revision_v = None, None, 1
    nickname = await get_nickname(userdata, bot_config.api)
    files_count_limit = userdata.metadata.download_count_limit
    keyboard = None
    has_music = False

    scheduler.create_task(
            remove_dir_and_file,
            [file_storage, message.conversation_message_id, message.from_id, config],
            (message.from_id, message.conversation_message_id),
            minutes=config.UFS.wait_for_delete_dir)

    if version:
        for x in raw_text:
            if version in x:
                raw_text.remove(x)
        version = version.split('.')
        major_v = version[0]
        build_v = version[1]
        revision_v = version[2] if len(version) > 2 else 1

    searching_files = await server.send_message(
            "files/searching",
            search_query='|'.join(raw_text),
            major_v=major_v,
            build_v=build_v,
            revision_v=revision_v
    )

    if searching_files.status:
        files_count = len(searching_files.content.files)
    else:
        await message.answer(localization[searching_files.error_msg].format(name=nickname))
        return

    if files_count == len(raw_text):
        # если количество файлов юзера == кол-ву найденных файлов, то отправляем файлы
        if files_count > files_count_limit:
            await message.answer(localization.TID_DOWNLOAD_FILES_WITHIN_LIMIT.format(name=nickname,
                                                                                     limit=files_count_limit,
                                                                                     files_count=files_count))
            files = searching_files.content.files[:files_count_limit]
        else:
            await message.answer(localization.TID_DOWNLOADFILES_START)
            files = searching_files.content.files

        has_music = any([file.endswith(('.ogg', '.mp3')) for file in files])
        path = bot_config.default_path / f"{message.from_id}/{message.conversation_message_id}/"
        path.mkdir(exist_ok=True, parents=True)

        result = await server.send_message(
                'files/downloading',
                game_data={
                    'path': str(path),
                    'search_query': '|'.join(files),
                    'major_v': major_v,
                    'build_v': build_v,
                    'revision_v': revision_v
                },
                metadata={'compress_to_archive': files_count > 5 or has_music}
        )

        result = [Path(i) for i in result.content]

        if files_count > 5:
            answer = localization.TID_STARTWORK_DONE.format(name=nickname)
        else:
            answer = ''
            for item in files:
                answer += localization.TID_DOWNLOADFILES_FILE.format(
                        file_name=item.split('/')[-1],
                        game_version=searching_files.content.version).split('\n')[0] + '\n'
            answer += localization.TID_DOWNLOADFILES_FILE.format(
                    file_name='',
                    game_version=searching_files.content.version).split('\n')[1] + '\n'

    else:
        # иначе отправляем список найденных файлов
        keyboard = server_downloads_keyboard(localization, message.conversation_message_id)
        path = Path(bot_config.default_path / f"{message.from_id}/{message.conversation_message_id}/")
        path.mkdir(exist_ok=True, parents=True)
        result = [path / 'files.txt']
        with result[0].open('w', encoding='utf-8') as f:
            f.write('\n'.join(item for item in searching_files.content.files))
            f.write('\n')
            f.write(searching_files.content.version)

        if files_count > 35:
            files = '\n'.join(item for item in searching_files.content.files[:35])
            answer = localization.TID_COMPACT_DOWNLOADFILES_TEXT.format(
                    name=nickname,
                    files_count=files_count,
                    game_version=searching_files.content.version,
                    files_name=files,
                    number=35
            )

        else:
            answer = localization.TID_DOWNLOADFILES_TEXT.format(
                    name=nickname,
                    files_count=files_count,
                    game_version=searching_files.content.version,
                    files_name='\n'.join(item for item in searching_files.content.files)
            )
            result = []

    result, loaded_by_user = await upload(result,
                                          user_api,
                                          bot_config.api,
                                          localization,
                                          message.peer_id,
                                          has_music)

    if loaded_by_user:
        await message.answer(answer, forward=result, keyboard=keyboard)
    else:
        await message.answer(answer, attachment=result, keyboard=keyboard)


@labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'command': 'remove_paths'}))
async def remove_paths_callback_handler(event: MessageEvent, localization):
    msg = await bot_config.api.messages.get_by_conversation_message_id(
            peer_id=event.peer_id,
            conversation_message_ids=event.conversation_message_id)

    attachments = None
    if msg.items[0].attachments:
        attachments = [get_valid_link(item) for item in msg.items[0].attachments]

    await event.edit_message(
            message='\n'.join([row.split('/')[-1] for row in msg.items[0].text.split('\n')]),
            keyboard=archive_with_all_files_keyboard(localization, event.conversation_message_id),
            attachment=attachments)
    await event.show_snackbar(localization.TID_DONE)


@labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'command': 'download_all_files'}))
async def get_all_files_callback_handler(
        event: MessageEvent, localization, server: Server, user_api, userdata, payload):
    path = bot_config.default_path / f'{event.user_id}/{payload.msg_id}/'

    if (path / 'files.txt').exists():
        await event.show_snackbar(localization.TID_DOWNLOADFILES_START)
        files = (path / 'files.txt').open('r').read().split('\n')
        has_music = any([file.endswith(('.ogg', '.mp3')) for file in files])
        major_v, build_v, revision_v = map(int, files[-1].split('.'))

        result = await server.send_message(
                'files/downloading',
                game_data={
                    'path': str(path),
                    'search_query': '|'.join(files[:-1]),
                    'major_v': major_v,
                    'build_v': build_v,
                    'revision_v': revision_v
                },
                metadata={
                    'compress_to_archive': len(files) - 1 > 5 or has_music}
        )
        if result:
            result = [Path(result.content)]
        else:
            await event.send_message(localization.TID_ERROR)
            return

        result, loaded_by_user = await upload(result,
                                              user_api,
                                              bot_config.api,
                                              localization,
                                              event.user_id,
                                              has_music)

        text = localization.TID_STARTWORK_DONE.format(name=await get_nickname(userdata, bot_config.api))
        if loaded_by_user:
            await event.send_message(text, forward=result, keyboard='[]')
        else:
            await event.send_message(text, attachment=result, keyboard='[]')

    else:
        await event.send_message(localization.TID_STARTWORK_FILENOTFOUND)
