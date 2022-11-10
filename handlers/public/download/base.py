from aiogram.types import Message


async def command_download(message: Message, user_localization):
    if not user_localization:
        return await message.answer(text='Подключение к серверу отсутствует!')

    await message.answer(user_localization.TID_COMMAND_IN_DEVELOPMENT)
