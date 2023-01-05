from aiogram.types import Message
from packets.base import Packet


async def command_sendmsg(message: Message, server):
    await server.send(
        Packet(12100, transport_id=server.events_handler.get_transport_id(),
               id=message.from_user.id, text="Ты позер!", count=5),
        no_answer=True
    )

    await message.answer(text=f"Отправляю...")


async def command_editmsg(message: Message, server):
    edit_this = await message.reply("Это сообщение отредачиться!")
    packet = await server.send(
        Packet(12101, transport_id=server.events_handler.get_transport_id(),
               message_id=edit_this.message_id, chat_id=edit_this.chat.id)
    )

    await edit_this.edit_text(text=packet.payload.text)
