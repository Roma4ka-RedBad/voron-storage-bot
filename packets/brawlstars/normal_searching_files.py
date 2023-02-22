from ..base import Packet
from database import FingerprintTable


# 13202
async def normal_brawlstars_search_files_query(instance, packet: Packet, game_manager, file_manager):
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
    _object.create_path()

    if not files:
        await file_manager.remove(_object=_object, forcibly_remove_job=True)
        await instance.client_connection.send(
            Packet(packet.pid, error_tid="DOWNLOADFILES_NOT_FOUND_ERROR")
        )

    else:
        await instance.client_connection.send(
            Packet(packet.pid, files=files, object_id=_object.object_id, files_count=len(files), path=_object.path,
                   version=f"{fingerprint.major_v}.{fingerprint.build_v}.{fingerprint.revision_v}")
        )
