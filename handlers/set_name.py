from aiogram.types import Message
from packets.base import Packet


async def command_setname(message: Message, server):
    nickname = message.text.split()
    nickname.pop(0)
    packet = await server.send(
        Packet(11101, tg_id=message.from_user.id, set_key="nickname", set_value="".join(nickname))
    )

    await message.answer(text=f"Твой новый ник {packet.payload.nickname}!")
