from aiogram.types import CallbackQuery

from keyboards.work import WorkCallback
from misc.file import DownloadedFile
from misc.server import Server


async def work_convert(cbq: CallbackQuery, server: Server, callback_data: WorkCallback):
    user = await server.send_message('user/get', {
        'tg_id': cbq.from_user.id
    })
    if not user:
        return await cbq.answer(text='Подключение к серверу отсутствует!')
    localization = await server.send_message(f'localization/{user.content.__data__.language_code}')

    if not cbq.message.reply_to_message:
        return await cbq.answer(localization.content.TID_STARTWORK_FILENOTFOUND)

    file = await DownloadedFile.get_file_by_index_or_name(cbq.message.reply_to_message, server,
                                                          file_name=cbq.message.reply_markup.inline_keyboard[
                                                              callback_data.row_index][0].text)
    if not file:
        return await cbq.answer(localization.content.TID_STARTWORK_FILENOTFOUND)
    await cbq.answer(localization.content.TID_STARTWORK)
