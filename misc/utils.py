import os
import shutil

from aiogram import Bot
from aiogram.types import BotCommand, Message, BotCommandScopeChat

from misc.models import Server, DFile, FilesStorage, IFile


async def download_file(message: Message, bot: Bot, server: Server, config):
    document = message.document
    if message.audio:
        document = message.audio

    if document.file_size < config.FILE_LIMITS.default_size * 1024 * 1024:
        main_dir = f"{config.UFS.path}{server.messenger}"
        user_dir = f"{message.from_user.id}/{message.message_id}"
        if not os.path.exists(f"{main_dir}/{user_dir}"):
            os.makedirs(f"{main_dir}/{user_dir}")

        file = await bot.get_file(document.file_id)
        shutil.copy(file.file_path, f"{main_dir}/{user_dir}/{document.file_name}")
        file = DFile(f"{main_dir}/{user_dir}/{document.file_name}", message)
        data = await server.send_msg("check_count", [{'path': str(file.path)}])
        return data.status, file, getattr(data, 'error_msg', None), data.content


async def create_ifile(message: Message, server: Server, config, server_response):
    main_dir = f"{config.UFS.path}{server.messenger}"
    user_dir = f"{message.from_user.id}/{message.message_id}"
    return IFile(f"{main_dir}/{user_dir}", message, server_response)


async def set_commands(bot: Bot, localization, chat_id: int):
    default = []
    for command in localization.TID_START_COMMANDS:
        default.append(BotCommand(command=command[0], description=command[1]))

    data = [
        (
            default,
            BotCommandScopeChat(chat_id=chat_id)
        )
    ]

    for commands_list, commands_scope in data:
        await bot.delete_my_commands(scope=commands_scope)
        await bot.set_my_commands(commands=commands_list, scope=commands_scope)


async def array_to_pages(array: dict, count: int = 6) -> dict:
    pages = {
        0: []
    }
    for element in array:
        last_page = list(pages)[-1]
        if len(pages[last_page]) == count:
            pages[last_page + 1] = [element]
        else:
            pages[last_page].append(element)
    return pages


async def safe_split_text(text: str, length: int = 4096, split_separator: str = ' ') -> list:
    temp_text = text
    parts = []
    while temp_text:
        if len(temp_text) > length:
            try:
                split_pos = temp_text[:length].rindex(split_separator)
            except ValueError:
                split_pos = length
            if split_pos < length // 4 * 3:
                split_pos = length
            parts.append(temp_text[:split_pos])
            temp_text = temp_text[split_pos:].lstrip()
        else:
            parts.append(temp_text)
            break
    return parts


async def delete_message_with_dir(file_id: int, fstorage: FilesStorage, bot: Bot):
    try:
        file = await fstorage.get(file_id)
        await fstorage.delete(file_id)
        shutil.rmtree(file.path.parent, ignore_errors=True)
        await bot.delete_message(file.message.chat.id, file.bot_answer.message_id)
        await bot.delete_message(file.message.chat.id, file.message.message_id)
    except:
        pass


async def delete_ifile(file_id: int, fstorage: FilesStorage):
    file = await fstorage.get(file_id)
    await fstorage.delete(file_id)
    shutil.rmtree(file.path, ignore_errors=True)
