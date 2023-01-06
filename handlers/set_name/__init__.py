from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from misc.states import UserStates
from misc.utils import easy_format


async def command_setname(message: Message, state: FSMContext, user_data, localization):
    await state.set_state(UserStates.wait_name)
    await message.answer(text=easy_format(localization.SETNAME_BODY,
                                          name=user_data.nickname or message.from_user.full_name))
