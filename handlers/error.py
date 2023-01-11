import traceback
from aiogram.types import Update
from packets.base import Packet


async def error_handler(update: Update, server):
    await server.send(Packet(12100, traceback_text=f"Ошибка в TG:\n{traceback.format_exc()}"), no_answer=True)
