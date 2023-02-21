import asyncio
import threading
from ..base import Packet
from managers.connections import ConnectionsManager
from database import FingerprintTable
from managers.models import Archive
from typing import Callable, Coroutine


# Я сделал это для сохранения твоего кода. Если оно нужно - можешь куда-нибудь это отсюда убрать
async def run_threadsafe(function: Coroutine | Callable, *args, **kwargs):
    if asyncio.iscoroutinefunction(function):
        function = function(*args, **kwargs)
    if asyncio.iscoroutine(function):
        new_loop = asyncio.new_event_loop()
        thread = threading.Thread(target=new_loop.run_forever)
        thread.start()
        future = asyncio.run_coroutine_threadsafe(function, new_loop)
        while not future.done():
            await asyncio.sleep(0.1)
        return future.result()

    else:
        return await asyncio.to_thread(function, *args, **kwargs)


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

        files = await game_manager.search_files(packet.payload.get('query') or _object.text_query, fingerprint.sha)
        _object.create_path()

        results = []
        divider = packet.payload.get('divider') or 3
        for file in files:
            results.append(await game_manager.download_file(fingerprint.sha, file, result_path=_object.path))
            if len(results) % divider == 0:
                await connections_manager.send_by_handlers(
                        Packet(20101, platform_name=_object.platform_name, message_id=packet.payload.message_id,
                               chat_id=_object.chat_id, tid="DOWNLOADFILES_START",
                               language_code=packet.payload.language_code,
                               form_args={'total_files_count': len(results), 'max_files_count': len(files)}))

        if packet.payload.get("compress_to_archive", None):
            results = await run_threadsafe(
                    Archive.compress_to_archive(str(_object.path / 'files.zip'), file_paths=results))

        await instance.client_connection.send(Packet(packet.pid, result=results))
        await file_manager.reload_task(_object.object_id)
    else:
        await instance.client_connection.send(Packet(packet.pid, error_tid="WORK_FILE_NOT_FOUND_ERROR"))
