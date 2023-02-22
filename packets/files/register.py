from ..base import Packet


# 14100
async def files_register(instance, packet: Packet, file_manager):
    if object_id := packet.payload.get('object_id'):
        _object = await file_manager.get(object_id)
    else:
        _object = await file_manager.register("file",
                                              user_message_id=packet.payload.message_id,
                                              chat_id=packet.payload.chat_id,
                                              platform_name=packet.payload.platform_name)
    _object.add_raw_files(*packet.payload.files)

    if _object.total_size > packet.payload.metadata.size_limit * 1024 * 1024:
        error_tid = "WORK_DOWNLOAD_MANY_FAIL_ERROR" if _object.last_raw_files_count > 1 else "WORK_DOWNLOAD_FAIL_ERROR"
        await instance.client_connection.send(
                Packet(packet.pid, error_tid=error_tid)
        )
        _object.rollback()

    else:
        await instance.client_connection.send(
                Packet(packet.pid, object_id=_object.object_id, path=_object.dir_path.resolve())
        )
