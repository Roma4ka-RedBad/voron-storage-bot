from dateutil import parser
from vkbottle import DocMessagesUploader
from vkbottle.bot import Message

from bot_config import Config
from misc.connections import ServerConnection
from misc.connections.downloads import download_raw_file
from misc.handler_utils import commands_to_regex
from misc.packets import Packet

labeler = Config.labelers.new()
labeler.vbml_ignore_case = True


@labeler.message(regexp=commands_to_regex('Об игре', 'About', 'about game'))
@labeler.private_message(text=('Об игре', 'About', 'about game'))
async def about_game_handler(message: Message, server: ServerConnection, localization):
    packet = await server.send(Packet(13101))
    if packet:
        game_date = parser.parse(packet.payload.ios.currentVersionReleaseDate)

        temp = await download_raw_file(packet.payload.ios.artworkUrl512)
        photo = await DocMessagesUploader(Config.bot_api).upload('logo.png', temp, peer_id=message.peer_id)

        await message.answer(
                message=localization.MARKET_BODY.format(
                        game_title=packet.payload.ios.trackName,
                        game_version=packet.payload.ios.version,
                        game_url_apple=packet.payload.ios.trackViewUrl,
                        game_url_android=packet.payload.android.link,
                        game_update_time=game_date.strftime('%H:%M %d.%m.%Y'),
                        game_update_desc=packet.payload.ios.releaseNotes
                ),
                attachment=photo
        )
    else:
        await event.send_message(localization.UNKNOWN_ERROR)
