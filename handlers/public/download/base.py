import re
from aiogram.types import Message, FSInputFile
from aiogram.utils.markdown import hcode, hbold

from misc.models import Server, FilesStorage, Scheduler
from misc.utils import safe_split_text, create_ifile, delete_ifile
from keyboards.download import download_kb


async def command_download(message: Message, server: Server, server_config, user_localization, user_data,
                           fstorage: FilesStorage, scheduler: Scheduler):
    if not server_config:
        return await message.answer(text='Подключение к серверу отсутствует!')

    raw_text = message.text.split()
    raw_text.pop(0)
    if raw_text:
        version = re.search("\d+[\.]\d+([\.]\d+)?", ''.join(raw_text))
        version = version[0] if version else None
        major_v, build_v, revision_v = None, None, 1
        if version:
            for x in raw_text:
                if version in x:
                    raw_text.remove(x)
            version = version.split('.')
            major_v = version[0]
            build_v = version[1]
            revision_v = version[2] if len(version) > 2 else 1

        searching_files = await server.send_msg("search_files", search_query=''.join(raw_text), major_v=major_v,
                                                build_v=build_v, revision_v=revision_v)
        if searching_files.status:
            file = await create_ifile(message, server, server_config, searching_files.content)
            file_id = await fstorage.put(file)

            if len(searching_files.content.files) > server_config.FILE_LIMITS.default_download_count:
                await message.answer_document(FSInputFile(await file.get_text_file()),
                                              caption=hbold(user_localization.TID_DOWNLOADFILES_FILES).format(
                                                  name=user_data.nickname or message.from_user.first_name,
                                                  files_count=len(searching_files.content.files),
                                                  game_version=searching_files.content.version
                                              ))
            elif len(searching_files.content.files) == 1:
                await message.answer_document(FSInputFile(await file.download(server)),
                                              caption=hbold(user_localization.TID_DOWNLOADFILES_FILE).format(
                                                  file_name=searching_files.content.files[0].split('/')[-1],
                                                  game_version=searching_files.content.version
                                              ))
            else:
                parts = await safe_split_text(user_localization.TID_DOWNLOADFILES_TEXT.format(
                    name=user_data.nickname or message.from_user.first_name,
                    files_count=len(searching_files.content.files),
                    game_version=searching_files.content.version,
                    files_name=''.join([f"\n  {hcode(file)}" for file in searching_files.content.files])
                ), split_separator='\n')

                reply_markup = None
                for part in parts:
                    if parts[-1] == part:
                        reply_markup = download_kb(user_localization, file_id)
                    await message.answer(hbold(part).replace('&lt;', '<').replace('&gt;', '>'), reply_markup=reply_markup)

            await scheduler.create_task(delete_ifile, [file_id, fstorage], file_id,
                                        minutes=server_config.UFS.wait_for_delete_dir)
        else:
            await message.answer(user_localization[searching_files.error_msg].format(
                name=user_data.nickname or message.from_user.first_name
            ))
    else:
        await message.answer(user_localization.TID_DOWNLOADFILES_QUERYMISSING.format(
            name=user_data.nickname or message.from_user.first_name
        ))
