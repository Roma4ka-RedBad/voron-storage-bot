from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    wait_name = State()
