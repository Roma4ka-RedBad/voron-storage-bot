from database import UserTable
from ..base import Packet


async def users_get(instance, packet: Packet):
    user = await UserTable.get_by_tg_or_vk(tg_id=packet.payload.tg_id)
    await instance.client_connection.send(
        Packet(packet.pid, user.__data__)
    )


async def users_set(instance, packet: Packet):
    user = await UserTable.get_by_tg_or_vk(tg_id=packet.payload.tg_id)
    setattr(user, packet.payload.set_key, packet.payload.set_value)
    await user.save()
    await instance.client_connection.send(Packet(packet.pid, user.__data__))
