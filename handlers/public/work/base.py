from aiogram import Bot
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from misc.models.server import Server
from misc.utils import download_file, get_keyboard
from keyboards.work import work_keyb


async def command_work(message: Message, server: Server, bot: Bot, scheduler: AsyncIOScheduler, server_config,
                       user_data, user_localization):
    if not server_config:
        return await message.reply(text='Подключение к серверу отсутствует!')

    if not message.document:
        return await message.reply(user_localization.TID_WORK_FILENOTEXIST.format(
            name=user_data.nickname or message.from_user.first_name
        ))

    file = await download_file(message, bot, server, server_config, scheduler)
    if not file:
        return await message.reply(user_localization.TID_WORK_DOWNLOADFALE.format(
            name=user_data.nickname or message.from_user.first_name
        ))

    if file.is_archive():
        return await message.reply(user_localization.TID_WORK_ISARCHIVE.format(
            name=user_data.nickname or message.from_user.first_name
        ), reply_markup=work_keyb(user_localization))

    keyboard = await get_keyboard(file, server)
    if not keyboard[0]:
        return await message.reply(user_localization[keyboard[1]].format(
            name=user_data.nickname or message.from_user.first_name
        ))

    return await message.reply(user_localization.TID_WORK_TEXT.format(
        name=user_data.nickname or message.from_user.first_name
    ), reply_markup=keyboard[1])
