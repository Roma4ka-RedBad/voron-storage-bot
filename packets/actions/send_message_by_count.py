from ..base import Packet


async def actions_send_message_by_count(instance, packet: Packet):
    connection = await instance.connections.get(transport_id=packet.payload.transport_id)
    await connection.send(Packet(packet.pid, packet.payload))
