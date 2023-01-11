import asyncio
from ..base import Packet
from managers.connections import ConnectionsManager
from database import FingerprintTable
from misc.utils import compress_to_archive


async def brawlstars_download_files_query(instance, packet: Packet, game_manager,
                                          file_manager, connections_manager: ConnectionsManager):
    _object = await file_manager.get(packet.payload.object_id)
    if _object:
        await file_manager.stop_task(_object.object_id)
        fingerprint = await FingerprintTable.get_or_none(FingerprintTable.major_v == _object.major_v,
                                                         FingerprintTable.build_v == _object.build_v,
                                                         FingerprintTable.revision_v == _object.revision_v)
        if not fingerprint:
            fingerprint = await FingerprintTable.get(is_actual=True)

        files = await game_manager.search_files(_object.text_query, fingerprint.sha)
        _object.create_path()
        results = []
        for file in files:
            results.append(await game_manager.download_file(fingerprint.sha, file, result_path=_object.path))
            if len(results) % 3 == 0:
                await connections_manager.send_by_handlers(
                    Packet(20101, platform_name=_object.platform_name, message_id=packet.payload.message_id,
                           chat_id=_object.chat_id, tid="DOWNLOADFILES_START",
                           language_code=packet.payload.language_code,
                           form_args={'total_files_count': len(results), 'max_files_count': len(files)}))

        if packet.payload.get("compress_to_archive", None):
            results = await (
                await asyncio.to_thread(compress_to_archive, str(_object.path / 'files.zip'), file_paths=results))

        await instance.client_connection.send(
            Packet(packet.pid, result=results)
        )
        await file_manager.reload_task(_object.object_id)
    else:
        await instance.client_connection.send(
            Packet(packet.pid, error_tid="WORK_FILE_NOT_FOUND_ERROR")
        )
