from ..base import Packet


# 14101
async def files_check(instance, packet: Packet, file_manager):
    _object = await file_manager.get(packet.payload.object_id)
    last_files_count = _object.register_files()
    if _object.total_files > packet.payload.metadata.files_count_limit:
        _object.rollback()
        await instance.client_connection.send(
                Packet(packet.pid, object_id=_object.object_id,
                       error_msg='WORK_TOO_MANY_FILES_ERROR',
                       files_count=_object.total_files_count + last_files_count,
                       maximum_count=packet.payload.metadata.files_count_limit)
        )
