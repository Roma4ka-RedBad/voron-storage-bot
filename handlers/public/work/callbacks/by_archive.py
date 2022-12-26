from aiogram.types import CallbackQuery

from keyboards.work import WorkCallback, work_converts_keyb
from misc.models import FilesStorage
from misc.utils import array_to_pages, check_server


async def work_by_archive(cbq: CallbackQuery, callback_data: WorkCallback, fstorage: FilesStorage,
                          user_data, user_localization):
    if not await check_server(cbq.message, user_localization):
        return

    file = await fstorage.get(callback_data.file_id)
    if not file:
        return await cbq.answer(user_localization.TID_STARTWORK_FILENOTFOUND)

    if not file.converts.status:
        return await cbq.message.reply(user_localization[file.converts.error_msg].format(
            name=user_data.nickname or cbq.from_user.first_name
        ))

    pages = file.converts.content[0]
    if callback_data.by_archive:
        pages = await array_to_pages(pages.converts.archive_files)

    return await cbq.message.edit_text(user_localization.TID_WORK_TEXT.format(
        name=user_data.nickname or cbq.from_user.first_name
    ), reply_markup=await work_converts_keyb(pages, file, callback_data.file_id, user_localization,
                                             callback_data.by_archive))
