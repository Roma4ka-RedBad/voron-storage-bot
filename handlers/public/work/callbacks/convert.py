import shutil

from aiogram.types import CallbackQuery, FSInputFile
from keyboards.work import WorkCallback

from misc.models import DownloadedFile, Server, Scheduler


async def work_convert(cbq: CallbackQuery, server: Server, callback_data: WorkCallback, scheduler: Scheduler,
                       server_config, user_data, user_localization):
    if not server_config:
        return await cbq.answer(text='Подключение к серверу отсутствует!')

    if not cbq.message.reply_to_message:
        return await cbq.answer(user_localization.TID_STARTWORK_FILENOTFOUND)

    file = await DownloadedFile.get_file_by_reply_message(cbq.message.reply_to_message, server_config, server)
    if not file:
        return await cbq.answer(user_localization.TID_STARTWORK_FILENOTFOUND)

    await cbq.answer(user_localization.TID_STARTWORK)
    scheduler.pause_task(file.user_dir)

    result = await server.send_msg(f'convert/{callback_data.to_format}', file={
        'path': file.get_dir(),
        'messenger': server.messenger,
        'target_file': cbq.message.reply_markup.inline_keyboard[callback_data.row_index][
            0].text if not callback_data.is_archive else None,
    }, metadata={'compress_to_archive': True})

    if result.status:
        if result.content.result:
            await cbq.message.reply_document(FSInputFile(result.content.result),
                                             caption=user_localization.TID_STARTWORK_DONE.format(
                                                 name=user_data.nickname or cbq.from_user.first_name
                                             ))
        else:
            await cbq.message.reply(user_localization.TID_STARTWORK_FILENOTCONVERT.format(
                name=user_data.nickname or cbq.from_user.first_name
            ))
        shutil.rmtree(result.content.process_dir)
    else:
        await cbq.message.reply(user_localization.TID_STARTWORK_FILENOTCONVERT.format(
            name=user_data.nickname or cbq.from_user.first_name
        ))
    scheduler.resume_task(file.user_dir)
