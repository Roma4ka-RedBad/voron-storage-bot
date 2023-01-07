from ..base import Packet
from managers.game import GameManager


async def brawlstars_search_files_query(instance, packet: Packet, game_manager: GameManager):
    await instance.client_connection.send(
        Packet(packet.pid, {})
    )
