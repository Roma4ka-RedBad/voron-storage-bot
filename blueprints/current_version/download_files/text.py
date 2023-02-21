from pathlib import Path

from keyboards import server_downloads_keyboard
from misc.connections.uploads import upload
from vkbottle.bot import Message

from bot_config import Config
from misc.connections import ServerConnection
from misc.custom_rules import StartFromRule
from misc.handler_utils import get_nickname, Regex, commands_to_regex
from misc.models import UserModel
from misc.packets import Packet

labeler = Config.labelers.new()
labeler.vbml_ignore_case = True


@labeler.message(regexp=commands_to_regex('скачать файл', 'download file', 'download', 'скачать', exactly=True))
@labeler.private_message(text=('скачать файл', 'download file', 'download', 'скачать'))
async def download_file_without_args_handler(message: Message, localization, userdata: UserModel):
    await message.answer(localization.DOWNLOADFILES_WITHOUT_ARGS.format(
            name=await get_nickname(userdata, Config.bot_api))
    )


@labeler.message(StartFromRule(regex_pattern=commands_to_regex(
        'скачать файл', 'download file', 'download', 'скачать', 'get', 'download')))
async def download_file_handler(message: Message, server: ServerConnection, userdata: UserModel, localization):
    raw_text = Regex(message.text).split(',| |\n')
    version = Regex(' '.join(raw_text)).search(r"\d+\.\d+(\.\d+)?")
    version = version[0] if version else None
    major_v, build_v, revision_v = None, None, 1
    nickname = await get_nickname(userdata)
    files_count_limit = userdata.metadata.download_count_limit

    keyboard = None
    has_music = False
    msg_id = None

    if version:
        for x in raw_text:
            if version in x:
                raw_text.remove(x)
        version = version.split('.')
        major_v = version[0]
        build_v = version[1]
        revision_v = version[2] if len(version) > 2 else 1

    packet = await server.send(
            Packet(13202, major_v=major_v, build_v=build_v, revision_v=revision_v, search_query='|'.join(raw_text),
                   message_id=message.message_id, chat_id=message.peer_id, platform_name="VK",
                   metadata=userdata.metadata))
    if packet:
        packet = packet.payload
    else:
        await message.answer(localization.DOWNLOADFILES_QUERY_MISSING_ERROR.format(
                name=await get_nickname(userdata)))
        return

    if packet.get("error_tid", None):
        await message.answer(message=localization[packet.error_tid].format(name=nickname),
                             name=await get_nickname(userdata))
        return

    # если количество файлов юзера == кол-ву найденных файлов, то отправляем файлы
    if packet.files_count == len(raw_text):
        if packet.files_count > files_count_limit:
            await message.answer(
                    localization.TID_DOWNLOAD_FILES_WITHIN_LIMIT.format(name=nickname,
                                                                        limit=files_count_limit,
                                                                        files_count=packet.files_count))
            files = packet.files[:files_count_limit]

        else:
            files = packet.files

        msg_id = (await message.answer(localization.DOWNLOADFILES_START.format(
                total_files_count=0,
                max_files_count=len(files)
        ))).conversation_message_id

        has_music = any([file.endswith(('.ogg', '.mp3')) for file in files])
        response = await server.send(
                Packet(13103,
                       object_id=packet.object_id,
                       message_id=msg_id,
                       language_code=userdata.language_code,
                       compress_to_archive=has_music or packet.files_count > 5,
                       divider=1))

        if response.payload.get('error_tid', None):
            await message.answer(localization[response.payload.error_tid])
            return

        if isinstance(response.payload.result, list):
            result = [Path(i) for i in response.payload.result]
            answer = ''
            for item in files:
                answer += localization.DOWNLOADFILES_FILE.format(
                        file_name=item.split('/')[-1],
                        game_version=packet.version).split('\n')[0] + '\n'
            answer += localization.DOWNLOADFILES_FILE.format(
                    file_name='',
                    game_version=packet.version).split('\n')[1] + '\n'

        else:
            result = [Path(response.payload.result)]
            if has_music:
                answer = localization.WORK_ARCHIVE_IS_RENAMED
            else:
                answer = localization.WORK_DONE_FOR_MANY_FILES.format(name=nickname)

        await Config.bot_api.messages.edit(message=localization.DOWNLOADFILES_UPLOAD,
                                           peer_id=message.peer_id, conversation_message_id=msg_id)

    # иначе отправляем список найденных файлов
    else:
        keyboard = server_downloads_keyboard(localization, packet.object_id, has_music, packet.files_count > 5,
                                             packet.files_count)
        path = Path(packet.path)
        result = [path / 'files.txt']
        with result[0].open('w', encoding='utf-8') as f:
            f.write('\n'.join(item for item in packet.files))
            f.write('\n')
            f.write(packet.version)

        if packet.files_count > 35:
            files = '\n'.join(item for item in packet.files[:35])
            answer = localization.DOWNLOADFILES_COMPACT_BODY.format(
                    name=nickname,
                    files_count=packet.files_count,
                    game_version=packet.version,
                    files_name=files,
                    number=35)

        else:
            answer = localization.TID_DOWNLOADFILES_TEXT.format(
                    name=nickname,
                    files_count=packet.files_count,
                    game_version=packet.version,
                    files_name='\n'.join(item for item in packet.files))
            result = []

    result, loaded_by_user = await upload(result,
                                          localization,
                                          message.peer_id,
                                          has_music)

    if loaded_by_user:
        await message.answer(answer, forward=result, keyboard=keyboard)
    else:
        await message.answer(answer, attachment=result, keyboard=keyboard)

    if msg_id:
        await Config.bot_api.messages.delete(delete_for_all=True, peer_id=message.peer_id, cmids=msg_id)
