from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message

from misc.models import Server
from misc.utils import check_server


async def setname_waitname(message: Message, server: Server, state: FSMContext, user_localization):
    await state.clear()
    user_data = await server.send_msg('user/set', tg_id=message.from_user.id, set_key='nickname', set_value=message.text)
    if not await check_server(message, user_data):
        return

    await message.answer(user_localization.TID_SETNAME_DONE.format(
        name=user_data.content.nickname
    ))
