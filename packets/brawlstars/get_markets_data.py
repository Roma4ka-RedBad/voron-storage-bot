from ..base import Packet
from managers.game import GameManager


async def brawlstars_get_markets_data(instance, packet: Packet, game_manager: GameManager):
    await instance.client_connection.send(
        Packet(
            packet.pid,
            ios=await game_manager.get_market_data(1),
            android=await game_manager.get_market_data(2)
        )
    )
