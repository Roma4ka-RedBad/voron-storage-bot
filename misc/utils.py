import os
import shutil

from aiogram import Bot
from aiogram.types.message import Message
from aiogram.types import BotCommand, BotCommandScopeDefault

from keyboards.work import work_converts_keyb
from misc.models import Server, DownloadedFile, Scheduler, FilesStorage


async def download_file(message: Message, bot: Bot, server: Server, config, scheduler: Scheduler, fstorage: FilesStorage):
    optimal_file_size = await server.send_msg(f"limit/{message.document.file_name.split('.')[-1]}")
    if message.document.file_size < optimal_file_size.content:
        main_dir = f"{config.UFS.path}{server.messenger}"
        user_dir = f"{message.from_user.id}/{message.message_id}"
        if not os.path.exists(f"{main_dir}/{user_dir}"):
            os.makedirs(f"{main_dir}/{user_dir}")

        file = await bot.get_file(message.document.file_id)
        await bot.download_file(file.file_path, f"{main_dir}/{user_dir}/{message.document.file_name}")
        scheduler.create_task(delete_message_with_dir, [f"{main_dir}/{user_dir}", message, bot], user_dir,
                              config.UFS.wait_for_delete_dir)

        return DownloadedFile(main_dir, user_dir, message.document.file_name)


async def get_keyboard(file: DownloadedFile, server: Server, condition: bool = None):
    converts = await server.send_msg('converts', [{
        'path': file.get_dir()
    }])

    return converts.status, converts.error_msg if not converts.status else await work_converts_keyb(converts.content,
                                                                                                    file, condition)


async def set_commands(bot: Bot, localization):
    default = []
    for command in localization.TID_START_COMMANDS:
        default.append(BotCommand(command=command[0], description=command[1]))

    data = [
        (
            default,
            BotCommandScopeDefault()
        )
    ]

    for commands_list, commands_scope in data:
        await bot.delete_my_commands(scope=commands_scope)
        await bot.set_my_commands(commands=commands_list, scope=commands_scope)


async def delete_message_with_dir(user_dir: str, message: Message, bot: Bot):
    try:
        shutil.rmtree(user_dir, ignore_errors=True)
        await bot.delete_message(message.chat.id, message.message_id + 1)
    except:
        pass
