import os

from aiogram import Bot
from aiogram.types.message import Message

from keyboards.work import work_keyb
from misc.server import Server
from misc.file import DownloadedFile


async def download_file(message: Message, bot: Bot, server: Server, main_dir: str):
    optimal_file_size = await server.send_message(f"limit/{message.document.file_name.split('.')[-1]}")
    if message.document.file_size < optimal_file_size.content:
        main_dir = f"{main_dir}{server.messenger}"
        user_dir = f"{message.from_user.id}/{message.message_id}"
        if not os.path.exists(f"{main_dir}/{user_dir}"):
            os.makedirs(f"{main_dir}/{user_dir}")

        file = await bot.get_file(message.document.file_id)
        await bot.download_file(file.file_path, f"{main_dir}/{user_dir}/{message.document.file_name}")
        return DownloadedFile(main_dir, user_dir, message.document.file_name)
    else:
        return None


async def get_buttons(file: DownloadedFile, server: Server):
    converts = await server.send_message('converts', data=[{
        'messenger': server.messenger,
        'name': file.get_dir()
    }])

    return converts.status, converts.error_msg if not converts.status else await work_keyb(converts.content, file)
