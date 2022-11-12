import os
import shutil
from typing import List, Tuple, Any
from vkbottle.bot import Message

from misc.connection.downloads import get_files
from misc.models import Scheduler, DownloadedFile, Server, FileModel, FileStorage
from misc.tools import remove_dir_and_file


async def download_files(message: Message,
                         server: Server,
                         file_objects: List[Tuple[str, Any]],
                         scheduler: Scheduler,
                         storage: FileStorage,
                         localization,
                         config) -> list[DownloadedFile] | None:
    main_dir = f"{config.UFS.path}{server.messenger}"
    user_dir = f"{message.from_id}/{message.conversation_message_id}"
    if not os.path.exists(f"{main_dir}/{user_dir}"):
        os.makedirs(f"{main_dir}/{user_dir}")
    scheduler.create_task(
        remove_dir_and_file,
        [storage, message.conversation_message_id, message.from_id, config],
        (message.from_id, message.conversation_message_id),
        minutes=config.UFS.wait_for_delete_dir)

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

        file = FileModel(
            name=filename, main_dir=main_dir, user_dir=user_dir, url=FileObject.url,
            ext=extension, size=size)

        prepared_files.append(file)

    if sum(file.size for file in prepared_files) > 1024*1024*1024:
        return None

    files =  await get_files(prepared_files)
    count = await server.send_message('check_count', [{'path': file.get_dir()} for file in files])
    if count.status:
        return files
    else:
        await message.reply(localization[count.error_msg].format(files_count=count.files_count,
                                                                 maximum_count=count.maximum_count))
        return None


async def remove_dir(user_id: int | str, dir_id: int | str, config):
    main_dir = f"{config.UFS.path}VK/"
    user_dir = f"{user_id}/{dir_id}/"
    shutil.rmtree(main_dir + user_dir)
