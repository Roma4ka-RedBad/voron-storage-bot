from aiogram.types import CallbackQuery, FSInputFile

from misc.models import Server, FilesStorage, Scheduler
from keyboards.download import DownloadCallback


async def download_archive(cbq: CallbackQuery, server: Server, callback_data: DownloadCallback, user_localization,
                           user_data, fstorage: FilesStorage, scheduler: Scheduler):
    if not user_localization:
        return await cbq.message.answer(text='Подключение к серверу отсутствует!')

    await cbq.message.edit_reply_markup(None)
    await scheduler.pause_task(callback_data.file_id)
    file = await fstorage.get(callback_data.file_id)
    if not file:
        return await cbq.answer(user_localization.TID_STARTWORK_FILENOTFOUND)

    message = await cbq.message.answer(user_localization.TID_DOWNLOADFILES_START)
    file = await file.download(server)
    if not file:
        return await cbq.message.answer(user_localization.TID_ERROR)

    await message.delete()
    await cbq.message.answer_document(FSInputFile(file), caption=user_localization.TID_STARTWORK_DONE.format(
        name=user_data.nickname or message.from_user.first_name
    ))
    await scheduler.resume_task(callback_data.file_id)
