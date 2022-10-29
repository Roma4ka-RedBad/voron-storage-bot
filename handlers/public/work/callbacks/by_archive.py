from aiogram.types import CallbackQuery

from keyboards.work import WorkCallback
from misc.utils import get_keyboard
from misc.models import DownloadedFile, Server


async def work_by_archive(cbq: CallbackQuery, server: Server, callback_data: WorkCallback, server_config, user_data, user_localization):
    if not server_config:
        return await cbq.answer(text='Подключение к серверу отсутствует!')

    if not cbq.message.reply_to_message:
        return await cbq.answer(user_localization.TID_STARTWORK_FILENOTFOUND)

    file = await DownloadedFile.get_file_by_reply_message(cbq.message.reply_to_message, server_config, server)
    if not file:
        await cbq.answer(user_localization.TID_STARTWORK_FILENOTFOUND)

    keyboard = await get_keyboard(file, server, callback_data.condition)
    if not keyboard[0]:
        return await cbq.message.edit_text(user_localization[keyboard[1]].format(
            name=user_data.nickname or cbq.from_user.first_name
        ))

    return await cbq.message.edit_text(user_localization.TID_WORK_TEXT.format(
            name=user_data.nickname or cbq.from_user.first_name
        ), reply_markup=keyboard[1])
