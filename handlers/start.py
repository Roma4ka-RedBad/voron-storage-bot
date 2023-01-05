from aiogram.types import Message


async def command_start(message: Message, user_data):
    await message.answer(text=f"Привет!\nТвой айди в боте: {user_data.id}\nТвой ник: {user_data.nickname}")
