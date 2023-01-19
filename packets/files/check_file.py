from ..base import Packet
from managers.models import Archive


async def files_check(instance, packet: Packet, file_manager):
    _object = await file_manager.get(packet.payload.object_id)
    if _object:
        if _object.is_archive():
            object_index = file_manager.objects.index(_object)
            file_manager.objects[object_index] = Archive(file_name=_object.file_name,
                                                         user_message_id=_object.user_message_id,
                                                         chat_id=_object.chat_id, platform_name=_object.platform_name,
                                                         object_id=_object.object_id)

            # Далее должна быть функция по подсчёту количества файлов в архиве
