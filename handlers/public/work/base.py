from aiogram import Bot
from aiogram.types import Message

from misc.models import Server, Scheduler, FilesStorage
from misc.utils import download_file, delete_message_with_dir
from keyboards.work import work_keyb, work_converts_keyb


async def command_work(message: Message, server: Server, bot: Bot, scheduler: Scheduler, server_config,
                       user_data, user_localization, fstorage: FilesStorage):
    if not server_config:
        return await message.reply(text='Подключение к серверу отсутствует!')

    file = await download_file(message, bot, server, server_config)
    if not file:
        return await message.reply(user_localization.TID_WORK_DOWNLOADFAIL.format(
            name=user_data.nickname or message.from_user.first_name
        ))
    file_id = await fstorage.put(file)
    await scheduler.create_task(delete_message_with_dir, [file_id, fstorage, bot], str(file_id),
                                minutes=server_config.UFS.wait_for_delete_dir)

    if file.is_archive():
        return await message.reply(user_localization.TID_WORK_ISARCHIVE.format(
            name=user_data.nickname or message.from_user.first_name
        ), reply_markup=work_keyb(user_localization, file_id))

    converts = await file.get_converts(server)
    if not converts.status:
        return await message.reply(user_localization[converts.error_msg].format(
            name=user_data.nickname or message.from_user.first_name
        ))

    return await message.reply(user_localization.TID_WORK_TEXT.format(
        name=user_data.nickname or message.from_user.first_name
    ), reply_markup=await work_converts_keyb(converts.content, file, file_id))
