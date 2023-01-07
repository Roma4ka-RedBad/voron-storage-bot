from ..base import Packet
from logic_objects.config import Config
from misc.localization import languages


async def client_get_config_data(instance, packet: Packet):
    await instance.client_connection.send(
        Packet(packet.pid, {"config": Config, "localization": languages})
    )
