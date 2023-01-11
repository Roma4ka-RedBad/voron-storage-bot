from ..base import Packet


async def brawlstars_get_markets_data(instance, packet: Packet, game_manager):
    await instance.client_connection.send(
        Packet(
            packet.pid,
            ios=await game_manager.get_market_data(1),
            android=await game_manager.get_market_data(2)
        )
    )
