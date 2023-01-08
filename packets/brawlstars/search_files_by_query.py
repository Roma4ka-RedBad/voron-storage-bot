from ..base import Packet
from managers.game import GameManager
from database import FingerprintTable


async def brawlstars_search_files_query(instance, packet: Packet, game_manager: GameManager, file_manager):
    fingerprint = await FingerprintTable.get_or_none(FingerprintTable.major_v == packet.payload.major_v,
                                                     FingerprintTable.build_v == packet.payload.build_v,
                                                     FingerprintTable.revision_v == packet.payload.revision_v)
    if not fingerprint:
        fingerprint = await FingerprintTable.get(is_actual=True)

    files = await game_manager.search_files(packet.payload.search_query, fingerprint.sha)
    _object = await file_manager.register("query", major_v=fingerprint.major_v, build_v=fingerprint.build_v,
                                          revision_v=fingerprint.revision_v, text_query=packet.payload.search_query,
                                          user_message_id=packet.payload.message_id,
                                          chat_id=packet.payload.chat_id,
                                          platform_name=packet.payload.platform_name)
    if not files:
        await file_manager.remove(_object=_object, forcibly_remove_job=True)
        await instance.client_connection.send(
            Packet(packet.pid, error_tid="DOWNLOADFILES_NOT_FOUND_ERROR")
        )
    elif len(files) > packet.payload.metadata.download_count_limit:
        file_path = await _object.create_text_document('\n'.join(files))
        await instance.client_connection.send(
            Packet(packet.pid, file=file_path, files_count=len(files),
                   version=f"{fingerprint.major_v}.{fingerprint.build_v}.{fingerprint.revision_v}")
        )
    elif len(files) == 1:
        _object.create_path()
        file_path = await game_manager.download_file(fingerprint.sha, files[0], _object.path)
        await instance.client_connection.send(
            Packet(packet.pid, downloaded_file=file_path, file_name=files[0],
                   version=f"{fingerprint.major_v}.{fingerprint.build_v}.{fingerprint.revision_v}")
        )
    else:
        await instance.client_connection.send(
            Packet(packet.pid, files=files, object_id=_object.object_id, files_count=len(files),
                   version=f"{fingerprint.major_v}.{fingerprint.build_v}.{fingerprint.revision_v}")
        )
