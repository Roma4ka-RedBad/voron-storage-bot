from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message

from states.user import UserStates


async def command_setname(message: Message, state: FSMContext, user_data, user_localization):
    if not user_data:
        return await message.answer(text='Подключение к серверу отсутствует!')

    await state.set_state(UserStates.wait_name)
    await message.answer(user_localization.TID_SETNAME_TEXT.format(
        name=user_data.nickname or message.from_user.first_name
    ))
