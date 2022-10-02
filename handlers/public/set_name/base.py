from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message

from states.user import UserStates
from misc.server import Server


async def command_setname(message: Message, server: Server, state: FSMContext):
    user = await server.send_message('user/get', {
        'tg_id': message.from_user.id
    })
    if not user:
        return await message.answer(text='Подключение к серверу отсутствует!')

    await state.set_state(UserStates.wait_name)
    await message.answer(f"{user.content.__data__.nickname or message.from_user.first_name}, как мне тебя называть?")
