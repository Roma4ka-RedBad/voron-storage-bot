import shutil

from aiogram.types import CallbackQuery, FSInputFile
from keyboards.work import WorkCallback
from misc.models.file import DownloadedFile
from misc.models.server import Server


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

    result = await server.send_message(f'convert/{callback_data.to_format}', {
        'name': file.get_dir(),
        'messenger': server.messenger
    })
    if result.status:
        await cbq.message.reply_document(FSInputFile(result.content.result_file), caption=localization.content.TID_STARTWORK_DONE % (
            user.content.__data__.nickname or cbq.from_user.first_name
        ))
        shutil.rmtree(result.content.process_dir)
    else:
        await cbq.message.reply(localization.content.TID_STARTWORK_FILENOTCONVERT % (
            user.content.__data__.nickname or cbq.from_user.first_name
        ))
