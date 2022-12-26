from aiogram import Bot
from aiogram.types import Message

from misc.models import Server, Scheduler, FilesStorage
from misc.utils import download_file, delete_message_with_dir, array_to_pages, check_server
from keyboards.work import work_converts_keyb


async def command_work(message: Message, server: Server, bot: Bot, scheduler: Scheduler, server_config,
                       user_data, user_localization, fstorage: FilesStorage):
    if not await check_server(message, user_localization):
        return

    file = await download_file(message, bot, server, server_config, user_data)
    if not file[0]:
        return await message.reply(user_localization[file[2]].format(**file[3]))
    file = file[1]

    file_id = await fstorage.put(file)
    await scheduler.create_task(delete_message_with_dir, [file_id, fstorage, bot], file_id,
                                minutes=server_config.UFS.wait_for_delete_dir)

    await file.get_converts(server)
    if not file.converts.status:
        return await message.reply(user_localization[file.converts.error_msg].format(
            name=user_data.nickname or message.from_user.first_name
        ))

    pages = file.converts.content[0]
    if file.is_archive():
        pages = await array_to_pages(pages.converts.archive_files)

    file.bot_answer = await message.reply(user_localization.TID_WORK_TEXT.format(
        name=user_data.nickname or message.from_user.first_name
    ), reply_markup=await work_converts_keyb(pages, file, file_id, user_localization,
                                             by_archive=file.is_archive()))
