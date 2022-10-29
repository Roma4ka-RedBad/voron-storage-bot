from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message

from misc.models import Server


async def setname_waitname(message: Message, server: Server, state: FSMContext, user_localization):
    await state.clear()
    user = await server.send_msg('user/set', tg_id=message.from_user.id, set_key='nickname', set_value=message.text)
    if not user:
        return await message.answer(text='Подключение к серверу отсутствует!')

    await message.answer(user_localization.TID_SETNAME_DONE.format(
        name=user.content.__data__.nickname
    ))
