from ..base import Packet


async def files_register(instance, packet: Packet, file_manager):
    if packet.payload.file_size > packet.payload.metadata.size_limit * 1024 * 1024:
        await instance.client_connection.send(
            Packet(packet.pid, error_tid="WORK_DOWNLOAD_FAIL_ERROR")
        )
    else:
        _object = await file_manager.register("file", file_name=packet.payload.file_name,
                                              user_message_id=packet.payload.message_id,
                                              chat_id=packet.payload.chat_id,
                                              platform_name=packet.payload.platform_name)
        _object.create_path()
        await instance.client_connection.send(
            Packet(packet.pid, object_id=_object.object_id, path=_object.dir_path.resolve())
        )
