import shutil
from aiogram import Bot
from aiogram.types import Message
from packets.base import Packet
from misc.utils import FormString


async def command_working(message: Message, bot: Bot, localization, user_data, server):
    document = message.document or message.audio
    packet = await server.send(
        Packet(14100, file_name=document.file_name, message_id=message.message_id, chat_id=message.chat.id,
               platform_name="TG", metadata=user_data.metadata, file_size=document.file_size))
    if packet:
        if packet.payload.get("error_tid", None):
            await message.answer(FormString.paste_args(localization[packet.payload.error_tid],
                                                       name=user_data.nickname or message.from_user.first_name))
        else:
            file = await bot.get_file(document.file_id)
            shutil.copy(file.file_path, f"{packet.payload.path}/{document.file_name}")
            await server.send(Packet(14101, object_id=packet.payload.object_id), no_answer=True)
