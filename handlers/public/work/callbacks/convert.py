import shutil

from aiogram.types import CallbackQuery, FSInputFile
from keyboards.work import WorkCallback

from misc.models import Server, Scheduler, FilesStorage


async def work_convert(cbq: CallbackQuery, server: Server, callback_data: WorkCallback, scheduler: Scheduler,
                       fstorage: FilesStorage, server_config, user_data, user_localization):
    if not server_config:
        return await cbq.answer(text='Подключение к серверу отсутствует!')

    file = await fstorage.get(callback_data.file_id)
    if not file:
        return await cbq.answer(user_localization.TID_STARTWORK_FILENOTFOUND)

    await cbq.answer(user_localization.TID_STARTWORK)
    await scheduler.pause_task(callback_data.file_id)
    convert_id = await fstorage.put_convert(callback_data.file_id)

    result = await server.send_msg(f'convert/{callback_data.to_format}', file={
        'path': str(file.path),
        'target_file': file.get_target_filename_by_index(callback_data.subfile_id)
    }, metadata={'compress_to_archive': True})
    print(result)

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

    await fstorage.delete_convert(convert_id)
    if not await fstorage.convert_worked(callback_data.file_id):
        await scheduler.reload_task(callback_data.file_id, minutes=server_config.UFS.wait_for_delete_dir)
        await scheduler.resume_task(callback_data.file_id)
