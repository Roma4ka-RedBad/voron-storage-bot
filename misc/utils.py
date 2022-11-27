import os
import aiohttp

from database import UserTable
from typing import List
from pathlib import Path
from logic_objects import FileObject, ArchiveObject, UserObject


async def get_user_db(data: UserObject) -> UserTable:
    user = None
    if data.vk_id is not None:
        user = UserTable.get_or_create(vk_id=data.vk_id)
    elif data.tg_id is not None:
        user = UserTable.get_or_create(tg_id=data.tg_id)

    return user


async def get_converts_by_file(file: FileObject):
    if archive := file.get_archive():
        archive_converts = {
            "archive_files": [
                {
                    "name": file.origin.filename,
                    "short_name": file.get_shortname(),
                    "converts": file.get_available_converts()
                }
                for file in archive.get_files() if file.get_available_converts()
            ],
            "archive_converts": archive.get_available_converts()
        }

        if len(archive_converts['archive_files']):
            return archive_converts
    else:
        return file.get_available_converts()


async def compress_to_archive(archive_path: str | Path,
                              files_objects: List[FileObject] = None,
                              file_paths: list = None):
    archive = ArchiveObject(FileObject.create(archive_path), "w", "zip", compresslevel=10)

    if files_objects:
        for file in files_objects:
            archive.write(file.path)

    if file_paths:
        for path in file_paths:
            if path:
                if os.path.isdir(path):
                    for folder, _, files in os.walk(path):
                        for _file in files:
                            archive.write(
                                os.path.join(folder, _file),
                                arc_name=os.path.join(folder.replace(path, ''), _file)
                            )
                else:
                    archive.write(path)

    return archive.close()


async def async_req(url: str, return_type: str, data=None):
    async with aiohttp.ClientSession() as session:
        if data:
            async with session.post(url, json=data) as resp:
                if resp.status == 200:
                    if return_type == 'bytes':
                        return await resp.content.read()
                    elif return_type == 'json':
                        return await resp.json()
                    elif return_type == 'text':
                        return await resp.text()
        else:
            async with session.get(url) as resp:
                if resp.status == 200:
                    if return_type == 'bytes':
                        return await resp.content.read()
                    elif return_type == 'json':
                        return await resp.json()
                    elif return_type == 'text':
                        return await resp.text()


async def create_response(status: bool, content = None, error_msg = None):
    response = {
        "status": status
    }

    if content:
        response['content'] = content

    if error_msg:
        response['error_msg'] = error_msg

    return response
