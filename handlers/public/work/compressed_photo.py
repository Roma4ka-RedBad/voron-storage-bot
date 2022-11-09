from aiogram.types import Message


async def compressed_photo(message: Message, user_localization):
    await message.answer(user_localization.TID_COMPRESSED_PHOTOS_TEXT)
