from ..base import Packet


async def files_register(instance, packet: Packet, file_manager):
    if object_id := packet.payload.get('object_id'):
        _object = await file_manager.get(object_id)
    else:
        _object = await file_manager.register("file",
                                              user_message_id=packet.payload.message_id,
                                              chat_id=packet.payload.chat_id,
                                              platform_name=packet.payload.platform_name)
    _object.add_raw_files(*packet.payload.files)

    if _object.total > packet.payload.metadata.size_limit * 1024 * 1024:
        await instance.client_connection.send(
                Packet(packet.pid, error_tid="WORK_DOWNLOAD_FAIL_ERROR")
        )
        _object.rollback()

    else:
        await instance.client_connection.send(
                Packet(packet.pid, object_id=_object.object_id, path=_object.dir_path.resolve())
        )
