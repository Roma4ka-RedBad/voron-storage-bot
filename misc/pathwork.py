from pathlib import Path
from typing import Iterable, Any

from vkbottle.bot import Message, MessageEvent

from bot_config import Config
from misc.connections import ServerConnection, Packet
from misc.connections.downloads import get_files
from misc.models import UserModel, FileModel


async def prepare_files(file_objects: list[tuple[str, Any]]) -> list[FileModel]:
    prepared_files = []
    for obj_type, FileObject in file_objects:
        if obj_type in 'photo':
            filename = FileObject.url.split('?')[0].split('/')[-1]
            extension = filename.split('.')[-1]
            size = 0

        elif obj_type == 'audio':
            filename = f'{FileObject.artist} - {FileObject.title}.mp3'
            extension = 'mp3'
            size = 0

        elif obj_type == 'doc':
            filename = FileObject.title
            extension = FileObject.ext
            size = FileObject.size

        else:
            continue

        prepared_files.append(FileModel(name=filename, url=FileObject.url, ext=extension, file_size=size))

    return prepared_files


async def download_and_register_files(files: list[FileModel] | list[tuple[str, Any]], server: ServerConnection,
                                      userdata: UserModel, localization, message: Message | MessageEvent = None,
                                      path_to_folder: str | Path = None, object_id: int = None) -> int | None:
    if not isinstance(files[0], FileModel):
        files = await prepare_files(files)
        packet = await server.send(Packet(14100,
                                          message_id=message.conversation_message_id, chat_id=message.peer_id,
                                          platform_name='VK', files=[dict(file) for file in files],
                                          object_id=object_id, metadata=userdata.metadata.dict()))
        if packet:
            if packet.payload.get('error_msg', None):
                await Config.bot_api.messages.send(message=localization[packet.payload.error_msg],
                                                   peer_id=message.peer_id, random_id=0)
                return
        else:
            await Config.bot_api.messages.send(message=localization.UNKNOWN_ERROR,
                                               peer_id=message.peer_id, random_id=0)
            return

        object_id = packet.payload.object_id
        path_to_folder = Path(packet.payload.path)

    if await get_files(files, path_to_folder) == 0:
        await Config.bot_api.messages.send(message=localization.UNKNOWN_ERROR)
        return

    packet = await server.send(Packet(14101, object_id=object_id, metadata=userdata.metadata.dict()))
    if packet:
        if packet.payload.get('error_msg', None):
            await Config.bot_api.messages.send(message=localization[packet.payload.error_msg],
                                               peer_id=message.peer_id, random_id=0)
            return

    return object_id
