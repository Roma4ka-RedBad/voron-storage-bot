from ..base import Packet


# 10100
async def client_data_by_handlers(instance, packet: Packet):
    instance.client_connection.is_handler = True
    await instance.client_connection.send(
        Packet(packet.pid, transport_id=instance.client_connection.transport_id)
    )
