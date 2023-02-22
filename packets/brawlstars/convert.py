from ..base import Packet
from managers.models import Archive


# 13104
async def convert(instance, packet: Packet, file_manager):
    _object = await file_manager.get(packet.payload.object_id)
    if _object:
        await file_manager.stop_task(_object.object_id)

        result = await _object.convert_to(packet.payload.convert_method)
        if result:
            if packet.payload.get("compress_to_archive", None):
                result = await Archive.compress_to_archive(str(_object.path / 'files.zip'), file_paths=result)
            await instance.client_connection.send(Packet(packet.pid, result=result))
        else:
            await instance.client_connection.send(Packet(packet.pid, error_tid="WORK_FILE_NOT_CONVERT_ERROR"))

    else:
        await instance.client_connection.send(Packet(packet.pid, error_tid="WORK_FILE_NOT_FOUND_ERROR"))
