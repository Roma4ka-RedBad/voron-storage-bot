from aiogram.types import CallbackQuery

from keyboards.work import WorkCallback, work_converts_keyb
from misc.models import Server, FilesStorage
from misc.utils import array_to_pages


async def work_by_archive(cbq: CallbackQuery, server: Server, callback_data: WorkCallback, fstorage: FilesStorage,
                          server_config, user_data, user_localization):
    if not server_config:
        return await cbq.answer(text='Подключение к серверу отсутствует!')

    file = await fstorage.get(callback_data.file_id)
    if not file:
        return await cbq.answer(user_localization.TID_STARTWORK_FILENOTFOUND)

    converts = await file.get_converts(server)
    if not converts.status:
        return await cbq.message.reply(user_localization[converts.error_msg].format(
            name=user_data.nickname or cbq.from_user.first_name
        ))

    if callback_data.by_archive:
        converts.content = await array_to_pages(converts.content.converts.archive_files * 3)

    return await cbq.message.edit_text(user_localization.TID_WORK_TEXT.format(
        name=user_data.nickname or cbq.from_user.first_name
    ), reply_markup=await work_converts_keyb(converts.content, file, callback_data.file_id, user_localization, callback_data.by_archive))