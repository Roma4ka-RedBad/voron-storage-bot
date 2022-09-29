from aiogram.types import CallbackQuery

from keyboards.work import WorkCallback


async def work_show_filename(cbq: CallbackQuery, callback_data: WorkCallback):
    return await cbq.answer(cbq.message.reply_markup.inline_keyboard[callback_data.row_index][0].text, cache_time=300)
