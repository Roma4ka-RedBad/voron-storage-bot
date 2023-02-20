from database import UserTable
from ..base import Packet


async def users_get(instance, packet: Packet):
    user = await UserTable.get_by_tg_or_vk(packet.payload)
    if user:
        await instance.client_connection.send(Packet(packet.pid, user.__data__))
    else:
        await instance.client_connection.send(Packet(packet.pid, None))


async def users_set(instance, packet: Packet):
    user = await UserTable.get_by_tg_or_vk(packet.payload)
    if user:
        setattr(user, packet.payload.set_key, packet.payload.set_value)
        await user.save()
        await instance.client_connection.send(Packet(packet.pid, user.__data__))
    else:
        await instance.client_connection.send(Packet(packet.pid, None))

