import asyncio
from ..base import Packet


async def actions_edit_message(instance, packet: Packet):
    connection = await instance.connections.get(transport_id=packet.payload.transport_id)
    for x in range(100):
        if (x + 1) % 5 == 0:
            await asyncio.sleep(1)
            await connection.send(Packet(packet.pid, message_id=packet.payload.message_id, text=f"[ {x+1}% ] Загрузка...", chat_id=packet.payload.chat_id))
        if (x + 1) == 100:
            await asyncio.sleep(0.5)
            await instance.client_connection.send(Packet(packet.pid, message_id=packet.payload.message_id, text="Готово!"))
                    