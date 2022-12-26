from aiogram.types import Message
from misc.utils import check_server


async def compressed_photo(message: Message, user_localization):
    if not await check_server(message, user_localization):
        return

    await message.answer(user_localization.TID_COMPRESSED_PHOTOS_TEXT)
