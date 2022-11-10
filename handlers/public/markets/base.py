from aiogram.types import Message
from aiogram.utils.markdown import hcode, hbold, hitalic
from dateutil import parser

from misc.models import Server


async def command_markets(message: Message, server: Server, user_data, user_localization):
    if not user_localization:
        return await message.answer(text='Подключение к серверу отсутствует!')

    markets = (await server.send_msg(f'markets/{user_data.language_code}')).content
    game_date = parser.parse(markets['1'].currentVersionReleaseDate)
    await message.answer_photo(markets['1'].artworkUrl512, caption=hbold(user_localization.TID_MARKET_TEXT).format(
        game_title=markets['1'].trackName,
        game_version=hcode(markets['1'].version),
        game_url_apple=markets['1'].trackViewUrl,
        game_url_android=markets['1'].trackViewUrl,
        game_update_time=hcode(game_date.strftime('%H:%M %d.%m.%Y')),
        game_update_desc=hitalic(markets['1'].releaseNotes)
    ))
