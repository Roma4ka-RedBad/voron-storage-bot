from aiogram.types import CallbackQuery

from keyboards.work import WorkCallback


async def work_convert(cbq: CallbackQuery, callback_data: WorkCallback):
    return await cbq.message.edit_text('Начинаю работу...')
