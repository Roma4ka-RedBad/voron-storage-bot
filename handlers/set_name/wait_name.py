from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from packets.base import Packet
from misc.utils import FormString


async def state_waitname(message: Message, server, state: FSMContext, localization):
    await state.clear()
    packet = await server.send(
        Packet(11101, tg_id=message.from_user.id, set_key="nickname", set_value=message.text)
    )
    if packet:
        await message.answer(text=FormString.paste_args(localization.SETNAME_DONE, name=packet.payload.nickname))
