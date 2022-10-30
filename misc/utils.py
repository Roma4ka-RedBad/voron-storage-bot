import os
import shutil

from aiogram import Bot
from aiogram.types.message import Message
from aiogram.types import BotCommand, BotCommandScopeDefault

from misc.models import Server, DownloadedFile, FilesStorage


async def download_file(message: Message, bot: Bot, server: Server, config):
    document = message.document
    if message.audio:
        document = message.audio

    optimal_file_size = await server.send_msg(f"limit/{document.file_name.split('.')[-1]}")
    if document.file_size < optimal_file_size.content:
        main_dir = f"{config.UFS.path}{server.messenger}"
        user_dir = f"{message.from_user.id}/{message.message_id}"
        if not os.path.exists(f"{main_dir}/{user_dir}"):
            os.makedirs(f"{main_dir}/{user_dir}")

        file = await bot.get_file(document.file_id)
        await bot.download_file(file.file_path, f"{main_dir}/{user_dir}/{document.file_name}")

        return DownloadedFile(f"{main_dir}/{user_dir}/{document.file_name}", message)


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


async def delete_message_with_dir(file_id: int, fstorage: FilesStorage, bot: Bot):
    try:
        file = await fstorage.get(file_id)
        await fstorage.delete(file_id)
        shutil.rmtree(file.path.parent, ignore_errors=True)
        await bot.delete_message(file.message.chat.id, file.message.message_id + 1)
    except:
        pass
