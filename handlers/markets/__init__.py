from aiogram.types import Message
from aiogram.utils.markdown import hcode, hitalic
from misc.utils import FormString
from dateutil import parser
from packets.base import Packet


async def command_markets(message: Message, localization, server):
    packet = await server.send(Packet(13101))
    if packet:
        game_date = parser.parse(packet.payload.ios.currentVersionReleaseDate)
        await message.answer_photo(packet.payload.ios.artworkUrl512,
                                   caption=FormString(localization.MARKET_BODY).get_form_string(
                                       game_title=packet.payload.ios.trackName,
                                       game_version=hcode(packet.payload.ios.version),
                                       game_url_apple=packet.payload.ios.trackViewUrl,
                                       game_url_android=packet.payload.android.link,
                                       game_update_time=hcode(game_date.strftime('%H:%M %d.%m.%Y')),
                                       game_update_desc=hitalic(packet.payload.ios.releaseNotes)
                                   ))
