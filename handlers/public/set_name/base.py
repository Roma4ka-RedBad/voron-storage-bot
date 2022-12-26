from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message

from misc.utils import check_server
from states.user import UserStates


async def command_setname(message: Message, state: FSMContext, user_data, user_localization):
    if not await check_server(message, user_localization):
        return

    await state.set_state(UserStates.wait_name)
    await message.answer(user_localization.TID_SETNAME_TEXT.format(
        name=user_data.nickname or message.from_user.first_name
    ))
