import os
import shutil
from typing import List, Tuple, Any
from vkbottle.bot import Message

from misc.server import Server
from misc.models.downloadable_file import File
from misc.connection.downloads import get_files


async def download_files(message: Message, server: Server, file_objects: List[Tuple[str, Any]], config):
    main_dir = f"{config.UFS.path}{server.messenger}"
    user_dir = f"{message.from_id}/{message.conversation_message_id}"
    if not os.path.exists(f"{main_dir}/{user_dir}"):
        os.makedirs(f"{main_dir}/{user_dir}")

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

        file = File(
            name=filename, main_dir=main_dir, user_dir=user_dir, url=FileObject.url,
            ext=extension, size=size)

        prepared_files.append(file)

    allowed_file_size = await server.send_message(f"limit/{prepared_files[0].ext}")
    if sum(file.size for file in prepared_files) > allowed_file_size.content:
        return None

    return await get_files(prepared_files)


async def remove_dir(user_id: int | str, dir_id: int | str, config):
    main_dir = f"{config.UFS.path}VK/"
    user_dir = f"{user_id}/{dir_id}/"
    shutil.rmtree(main_dir + user_dir)
