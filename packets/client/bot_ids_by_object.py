from ..base import Packet


#10102
async def client_bot_ids_by_object(instance, packet: Packet, file_manager):
    _object = await file_manager.get(packet.payload.object_id)
    if _object:
        _object.bot_message_ids = packet.payload.message_ids
