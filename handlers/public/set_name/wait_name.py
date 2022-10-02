from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message

from misc.server import Server


async def setname_waitname(message: Message, server: Server, state: FSMContext):
    await state.clear()
    user = await server.send_message('user/set', {
        'tg_id': message.from_user.id,
        'set_key': 'nickname',
        'set_value': message.text
    })
    if not user:
        return await message.answer(text='Подключение к серверу отсутствует!')

    await message.answer(f"Хорошо, теперь я буду тебя называть {user.content.__data__.nickname or message.from_user.first_name}!")
