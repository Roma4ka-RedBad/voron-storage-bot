import traceback
from aiogram.types.error_event import ErrorEvent
from packets.base import Packet


async def error_handler(error: ErrorEvent, server, localization):
    if message := error.update.message:
        await message.answer(localization.UNKNOWN_ERROR)
    elif cbq := error.update.callback_query:
        await cbq.answer(localization.UNKNOWN_ERROR)

    await server.send(Packet(12100, traceback_text=f"Ошибка в TG:\n{traceback.format_exc()}"), no_answer=True)
