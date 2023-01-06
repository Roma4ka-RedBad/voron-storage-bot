from aiogram.types import Message


async def compressed_photo(message: Message, localization):
    await message.answer(localization.WORK_COMPRESSED_PHOTOS)
