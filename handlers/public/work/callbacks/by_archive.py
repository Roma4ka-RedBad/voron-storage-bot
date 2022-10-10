from aiogram.types import CallbackQuery

from keyboards.work import WorkCallback
from misc.utils import get_buttons
from misc.models.file import DownloadedFile
from misc.models.server import Server


async def work_by_archive(cbq: CallbackQuery, server: Server, callback_data: WorkCallback):
    user = await server.send_message('user/get', {
        'tg_id': cbq.from_user.id
    })
    if not user:
        return await cbq.answer(text='Подключение к серверу отсутствует!')
    localization = await server.send_message(f'localization/{user.content.__data__.language_code}')

    if not cbq.message.reply_to_message:
        return await cbq.answer(localization.content.TID_STARTWORK_FILENOTFOUND)

    file = await DownloadedFile.get_file_by_index_or_name(cbq.message.reply_to_message, server,
                                                          file_name=cbq.message.reply_to_message.document.file_name)
    if not file:
        await cbq.answer(localization.content.TID_STARTWORK_FILENOTFOUND)

    keyboard = await get_buttons(file, server, callback_data.condition)
    if not keyboard[0]:
        return await cbq.message.edit_text(localization.content[keyboard[1]] % (
                user.content.__data__.nickname or cbq.from_user.first_name
        ))

    return await cbq.message.edit_text(localization.content.TID_WORK_TEXT % (
            user.content.__data__.nickname or cbq.from_user.first_name
    ), reply_markup=keyboard[1])
